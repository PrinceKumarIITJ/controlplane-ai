import uuid
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.schemas.governance import (
    AgentAction, GovernanceDecisionResponse, RiskAssessment,
    PolicyContext, CanonicalDecision, AssuranceLevel
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
        # Performance / Grounding Engine
        claim_text = str(action.parameters.get("claim_text", action.target))
        evidence_chunks = action.parameters.get("evidence_chunks", [])
        perf_risk, grounding_status, perf_conf = PerformanceEngine.evaluate_grounding(claim_text, evidence_chunks)

        # Cost Engine
        cost_risk, est_cost, exp_cost, cost_dev = CostEngine.evaluate_cost_risk(action.parameters)

        # Responsibility Engine
        payload_text = f"{action.target} {json.dumps(action.parameters)}"
        resp_risk, violations, resp_conf = ResponsibilityEngine.evaluate_responsibility(payload_text)

        # Combined Detection Confidence
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

        # Determine Action Status
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
