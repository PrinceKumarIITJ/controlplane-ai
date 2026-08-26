import uuid
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.schemas.governance import (
    AgentAction, GovernanceDecisionResponse, RiskAssessment,
    PolicyContext, CanonicalDecision, AssuranceLevel,
    AIResponsePayload, ResponseGovernanceResponse
)
from app.models.domain import AgentActionModel, DecisionModel
from app.engines.policy_engine import PolicyEngine
from app.engines.business_impact import BusinessImpactEngine
from app.engines.performance import PerformanceEngine
from app.engines.cost import CostEngine
from app.engines.responsibility import ResponsibilityEngine
from app.engines.risk import RiskEngine
from app.engines.decision import DecisionEngine
from app.services.assurance_router import AssuranceRouter
from app.services.token_service import TokenService
from app.services.audit_service import AuditService
from app.services.db_service import DBService
from app.core.crypto import compute_parameters_hash

class InterceptorService:
    @staticmethod
    def govern_action(
        db: Session,
        action: AgentAction
    ) -> GovernanceDecisionResponse:
        request_id = f"req_{uuid.uuid4().hex[:10]}"
        decision_id = f"dec_{uuid.uuid4().hex[:10]}"
        params_hash = compute_parameters_hash(action.parameters)

        # 1. Load active policy
        policy = PolicyEngine.load_policy(db, action.requester.application_id)
        policy_id = policy.get("policy_id", "DEFAULT_POLICY")
        policy_version = policy.get("version", "1.0.0")

        # 2. Business Impact Engine
        bi_score = BusinessImpactEngine.calculate_impact(action)

        # 3. Assurance Router
        assurance_level = AssuranceRouter.determine_assurance_level(action, bi_score, policy)

        # 4. Execute Inspection Engines
        claim_text = str(action.parameters.get("claim_text", action.target))
        evidence_chunks = action.parameters.get("evidence_chunks", [])
        perf_risk, grounding_status, perf_conf = PerformanceEngine.evaluate_grounding(claim_text, evidence_chunks)

        cost_risk, est_cost, exp_cost, cost_dev = CostEngine.evaluate_cost_risk(action.parameters)

        payload_text = f"{action.target} {json.dumps(action.parameters)}"
        resp_risk, violations, resp_conf = ResponsibilityEngine.evaluate_responsibility(payload_text)

        detection_confidence = round((perf_conf + resp_conf) / 2.0, 4)

        # 5. Composite Risk Engine
        risk_assessment = RiskEngine.calculate_composite_risk(
            performance_risk=perf_risk,
            cost_risk=cost_risk,
            responsibility_risk=resp_risk,
            business_impact=bi_score,
            detection_confidence=detection_confidence,
            policy=policy
        )

        # 6. Decision Precedence Engine
        canonical_decision, warning, rule_triggered, reason = DecisionEngine.evaluate_decision(
            assurance_level=assurance_level,
            risk_assessment=risk_assessment,
            grounding_status=grounding_status,
            cost_deviation=cost_dev,
            policy=policy
        )

        if canonical_decision == CanonicalDecision.ALLOW:
            action_status = "AUTHORIZED"
        elif canonical_decision == CanonicalDecision.HUMAN_REVIEW:
            action_status = "PENDING_REVIEW"
        else:
            action_status = "BLOCKED"

        # 7. Persist Action to DB
        action_model = AgentActionModel(
            action_id=action.action_id,
            action_type=action.action_type.value,
            target=action.target,
            parameters_hash=params_hash,
            parameters_json=json.dumps(action.parameters),
            agent_id=action.requester.agent_id,
            user_id=action.requester.user_id,
            application_id=action.requester.application_id,
            business_impact=bi_score,
            reversibility=action.reversibility.value,
            status=action_status
        )
        DBService.save_action(db, action_model)

        # 8. Persist Decision to DB
        decision_model = DecisionModel(
            decision_id=decision_id,
            action_id=action.action_id,
            assurance_level=assurance_level.value,
            performance_risk=risk_assessment.performance_risk,
            cost_risk=risk_assessment.cost_risk,
            responsibility_risk=risk_assessment.responsibility_risk,
            business_impact=risk_assessment.business_impact,
            detection_confidence=risk_assessment.detection_confidence,
            composite_risk=risk_assessment.composite_risk,
            decision=canonical_decision.value,
            warning=warning,
            policy_id=policy_id,
            policy_version=policy_version,
            reason=reason,
            rule_triggered=rule_triggered
        )
        DBService.save_decision(db, decision_model)

        # 9. Issue Approval Token if ALLOWed
        token_str = None
        if canonical_decision == CanonicalDecision.ALLOW:
            token_str = TokenService.issue_token_for_action(db, action_model, decision_model)

        # 10. Audit Logging
        AuditService.log_event(
            db=db,
            request_id=request_id,
            application_id=action.requester.application_id,
            agent_id=action.requester.agent_id,
            user_id=action.requester.user_id,
            action_type=action.action_type.value,
            assurance_level=assurance_level.value,
            decision=canonical_decision.value,
            policy_id=policy_id,
            policy_version=policy_version,
            event_type="ACTION_GOVERNANCE_EVALUATED",
            payload={
                "action_id": action.action_id,
                "rule_triggered": rule_triggered,
                "composite_risk": risk_assessment.composite_risk,
                "token_issued": bool(token_str)
            }
        )

        return GovernanceDecisionResponse(
            request_id=request_id,
            action_id=action.action_id,
            assurance_level=assurance_level,
            risk_assessment=risk_assessment,
            decision=canonical_decision,
            warning=warning,
            policy_context=PolicyContext(
                policy_id=policy_id,
                policy_version=policy_version,
                rule_triggered=rule_triggered
            ),
            reason=reason,
            approval_token=token_str,
            status=action_status
        )

    @staticmethod
    def govern_response(
        db: Session,
        response_payload: AIResponsePayload
    ) -> ResponseGovernanceResponse:
        """
        FLOW A: AI Response Governance (Informational query check against knowledge base & policy).
        """
        request_id = f"req_{uuid.uuid4().hex[:10]}"
        policy = PolicyEngine.load_policy(db, response_payload.application_id)
        policy_id = policy.get("policy_id", "DEFAULT_POLICY")
        policy_version = policy.get("version", "1.0.0")

        # 1. Performance / Grounding Engine
        perf_risk, grounding_status, perf_conf = PerformanceEngine.evaluate_grounding(
            response_payload.response_text,
            response_payload.evidence_context
        )

        # 2. Cost Engine
        cost_params = {"estimated_tokens": len(response_payload.prompt.split()) + len(response_payload.response_text.split()), "agent_loops": 1}
        cost_risk, est_cost, exp_cost, cost_dev = CostEngine.evaluate_cost_risk(cost_params)

        # 3. Responsibility Engine
        full_text = f"{response_payload.prompt} {response_payload.response_text}"
        resp_risk, violations, resp_conf = ResponsibilityEngine.evaluate_responsibility(full_text)

        # Combined Detection Confidence
        detection_confidence = round((perf_conf + resp_conf) / 2.0, 4)
        bi_score = 10.0 if grounding_status == "SUPPORTED" else 45.0

        # Composite Risk Engine
        risk_assessment = RiskEngine.calculate_composite_risk(
            performance_risk=perf_risk,
            cost_risk=cost_risk,
            responsibility_risk=resp_risk,
            business_impact=bi_score,
            detection_confidence=detection_confidence,
            policy=policy
        )

        # Decision Engine
        if resp_risk >= 0.80:
            canonical_decision = CanonicalDecision.BLOCK
            rule_triggered = "HARD_SECURITY_VIOLATION"
            reason = "Response contains severe policy or safety violation."
            intervention = "RESPONSE_BLOCKED: Security or PII violation detected."
        elif grounding_status in ["UNVERIFIED", "CONTRADICTED"] or detection_confidence < 0.60:
            canonical_decision = CanonicalDecision.RECHECK
            rule_triggered = "UNGROUNDED_CLAIM_RECHECK"
            reason = "AI response contains unsupported or unverified policy claim."
            intervention = "FLAGGED_FOR_RECHECK: Claim cannot be grounded against policy evidence."
        else:
            canonical_decision = CanonicalDecision.ALLOW
            rule_triggered = "SUPPORTED_RESPONSE_ALLOW"
            reason = "AI response satisfied all grounding, responsibility, and cost policy checks."
            intervention = "RESPONSE_APPROVED: Fully grounded and verified."

        # Audit Logging
        AuditService.log_event(
            db=db,
            request_id=request_id,
            application_id=response_payload.application_id,
            agent_id="ai_llm_app",
            user_id="end_user",
            action_type="RESPONSE_GOVERNANCE",
            assurance_level="L1" if grounding_status == "SUPPORTED" else "L2",
            decision=canonical_decision.value,
            policy_id=policy_id,
            policy_version=policy_version,
            event_type="RESPONSE_GOVERNANCE_EVALUATED",
            payload={
                "response_id": response_payload.response_id,
                "grounding_status": grounding_status,
                "rule_triggered": rule_triggered,
                "intervention": intervention
            }
        )

        return ResponseGovernanceResponse(
            request_id=request_id,
            response_id=response_payload.response_id,
            assurance_level=AssuranceLevel.L1 if grounding_status == "SUPPORTED" else AssuranceLevel.L2,
            risk_assessment=risk_assessment,
            grounding_status=grounding_status,
            decision=canonical_decision,
            warning=(canonical_decision != CanonicalDecision.ALLOW),
            policy_context=PolicyContext(
                policy_id=policy_id,
                policy_version=policy_version,
                rule_triggered=rule_triggered
            ),
            reason=reason,
            intervention=intervention
        )
