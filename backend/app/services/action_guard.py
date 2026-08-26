import time
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.core.crypto import verify_approval_token_signature, compute_parameters_hash
from app.services.db_service import DBService

class ActionGuard:
    @staticmethod
    def validate_and_consume_token(
        db: Session,
        token_str: Optional[str],
        expected_action_id: str,
        expected_target: str,
        request_parameters: Dict[str, Any]
    ) -> Tuple[bool, int, str, int]:
        """
        Enforces strict target execution boundary checks.
        Returns: (is_valid, http_status_code, message, target_api_calls_increment)
        """
        # 1. Missing token check
        if not token_str:
            return False, 403, "Authorization Denied: Missing ControlPlane Approval Token header", 0

        # 2. Cryptographic signature check
        is_sig_valid, payload, sig_error = verify_approval_token_signature(token_str)
        if not is_sig_valid or not payload:
            return False, 401, f"Authorization Denied: {sig_error}", 0

        # 3. Expiration TTL check
        now = int(time.time())
        if payload.get("expires_at", 0) < now:
            return False, 401, "Authorization Denied: Expired Approval Token", 0

        # 4. Action ID binding check
        if payload.get("action_id") != expected_action_id:
            return False, 401, f"Authorization Denied: Action ID mismatch (token={payload.get('action_id')}, expected={expected_action_id})", 0

        # 5. Target binding check
        if payload.get("target") != expected_target:
            return False, 401, f"Authorization Denied: Target mismatch (token={payload.get('target')}, expected={expected_target})", 0

        # 6. Parameter hash integrity check
        computed_hash = compute_parameters_hash(request_parameters)
        if payload.get("parameters_hash") != computed_hash:
            return False, 401, "Authorization Denied: Parameter tampering detected (parameters_hash mismatch)", 0

        # 7. Database Nonce lookup & single-use replay check
        nonce = payload.get("nonce")
        token_model = DBService.get_token_by_nonce(db, nonce)
        if not token_model:
            return False, 401, "Authorization Denied: Nonce not recognized in token database", 0

        if token_model.status == "CONSUMED":
            return False, 401, "Authorization Denied: Token replay attack detected (Token nonce already consumed)", 0

        if token_model.status != "ISSUED":
            return False, 401, f"Authorization Denied: Token status is {token_model.status}", 0

        # 8. Decision state verification
        decision_model = DBService.get_decision(db, payload.get("decision_id"))
        if not decision_model:
            return False, 403, "Authorization Denied: Associated governance decision not found", 0

        # Verify policy version binding
        if decision_model.policy_version != payload.get("policy_version"):
            return False, 401, "Authorization Denied: Policy version binding mismatch", 0

        # 9. Atomic Token Consumption
        token_model.status = "CONSUMED"
        token_model.consumed_at = datetime.utcnow()
        DBService.update_action_status(db, expected_action_id, "EXECUTED")
        db.commit()

        return True, 200, "Authorization Verified: Target action execution approved", 1
