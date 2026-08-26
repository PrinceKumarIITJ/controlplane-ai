import time
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.core.crypto import generate_approval_token, compute_parameters_hash
from app.models.domain import ApprovalTokenModel, DecisionModel, AgentActionModel
from app.services.db_service import DBService

class TokenService:
    @staticmethod
    def issue_token_for_action(
        db: Session,
        action: AgentActionModel,
        decision: DecisionModel
    ) -> str:
        """
        Generates and saves a single-use ApprovalTokenModel to DB for an ALLOWed or APPROVED action.
        """
        now = int(time.time())
        expires_at = now + settings.TOKEN_TTL_SECONDS
        nonce = f"n_{uuid.uuid4().hex[:12]}"
        token_id = f"tok_{uuid.uuid4().hex[:10]}"

        params_dict = DBService.get_action(db, action.action_id).parameters_json
        parameters_hash = action.parameters_hash

        payload = {
            "token_id": token_id,
            "action_id": action.action_id,
            "action_type": action.action_type,
            "target": action.target,
            "parameters_hash": parameters_hash,
            "decision_id": decision.decision_id,
            "application_id": action.application_id,
            "policy_id": decision.policy_id,
            "policy_version": decision.policy_version,
            "nonce": nonce,
            "issued_at": now,
            "expires_at": expires_at
        }

        signature_str = generate_approval_token(payload)

        token_model = ApprovalTokenModel(
            token_id=token_id,
            action_id=action.action_id,
            decision_id=decision.decision_id,
            parameters_hash=parameters_hash,
            signature=signature_str,
            nonce=nonce,
            policy_id=decision.policy_id,
            policy_version=decision.policy_version,
            issued_at=now,
            expires_at=expires_at,
            status="ISSUED"
        )

        DBService.save_token(db, token_model)
        return signature_str
