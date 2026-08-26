import uuid
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.schemas.governance import ReviewAction, HumanReviewRequest
from app.models.domain import HumanReviewModel, DecisionModel, AgentActionModel
from app.services.db_service import DBService
from app.services.token_service import TokenService
from app.services.audit_service import AuditService

class ReviewService:
    @staticmethod
    def process_human_review(
        db: Session,
        action_id: str,
        review_request: HumanReviewRequest
    ) -> Tuple[bool, str, Optional[str], Optional[Dict[str, Any]]]:
        """
        Processes human review (APPROVE, REJECT, OVERRIDE).
        If APPROVED or OVERRIDDEN: generates HMAC Approval Token and updates action status to AUTHORIZED.
        If REJECTED: updates action status to REJECTED with zero tokens generated.
        Returns: (success, message, token_or_none, updated_action_dict)
        """
        action = DBService.get_action(db, action_id)
        if not action:
            return False, f"Action ID '{action_id}' not found.", None, None

        if action.status not in ["PENDING_REVIEW", "AUTHORIZED", "REJECTED"]:
            return False, f"Action status is '{action.status}' and cannot be reviewed.", None, None

        decision = DBService.get_decision_by_action(db, action_id)
        if not decision:
            return False, f"Governance decision for action '{action_id}' not found.", None, None

        review_id = f"rev_{uuid.uuid4().hex[:10]}"
        review_model = HumanReviewModel(
            review_id=review_id,
            action_id=action_id,
            decision_id=decision.decision_id,
            reviewer_id=review_request.reviewer_id,
            review_action=review_request.review_action.value,
            reason=review_request.reason,
            policy_id=decision.policy_id,
            policy_version=decision.policy_version
        )
        DBService.save_review(db, review_model)

        if review_request.review_action in [ReviewAction.APPROVE, ReviewAction.OVERRIDE]:
            DBService.update_action_status(db, action_id, "AUTHORIZED")
            token_str = TokenService.issue_token_for_action(db, action, decision)

            # Audit event
            AuditService.log_event(
                db=db,
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                application_id=action.application_id,
                agent_id=action.agent_id,
                user_id=action.user_id,
                action_type=action.action_type,
                assurance_level=decision.assurance_level,
                decision=decision.decision,
                policy_id=decision.policy_id,
                policy_version=decision.policy_version,
                event_type=f"HUMAN_REVIEW_{review_request.review_action.value}",
                payload={
                    "review_id": review_id,
                    "reviewer_id": review_request.reviewer_id,
                    "action_id": action_id,
                    "token_issued": True
                }
            )
            return True, f"Action '{action_id}' approved by human reviewer. Approval Token issued.", token_str, {
                "action_id": action_id,
                "status": "AUTHORIZED",
                "review_action": review_request.review_action.value
            }

        else: # REJECT
            DBService.update_action_status(db, action_id, "REJECTED")

            # Audit event
            AuditService.log_event(
                db=db,
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                application_id=action.application_id,
                agent_id=action.agent_id,
                user_id=action.user_id,
                action_type=action.action_type,
                assurance_level=decision.assurance_level,
                decision=decision.decision,
                policy_id=decision.policy_id,
                policy_version=decision.policy_version,
                event_type="HUMAN_REVIEW_REJECT",
                payload={
                    "review_id": review_id,
                    "reviewer_id": review_request.reviewer_id,
                    "action_id": action_id,
                    "token_issued": False
                }
            )
            return True, f"Action '{action_id}' rejected by human reviewer. No token issued.", None, {
                "action_id": action_id,
                "status": "REJECTED",
                "review_action": review_request.review_action.value
            }
