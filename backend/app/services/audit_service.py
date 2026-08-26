import json
import hashlib
import uuid
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.domain import AuditEventModel
from app.services.db_service import DBService

class AuditService:
    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    @staticmethod
    def redact_sensitive_data(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Redacts raw secrets and credentials from audit payloads."""
        payload_str = json.dumps(payload)
        # Mask emails, SSNs, and SK tokens
        payload_str = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[REDACTED_SECRET]', payload_str)
        payload_str = re.sub(r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]', payload_str)
        payload_str = re.sub(r'bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*', 'Bearer [REDACTED_TOKEN]', payload_str, flags=re.IGNORECASE)
        return json.loads(payload_str)

    @classmethod
    def compute_event_hash(cls, canonical_payload_str: str, previous_hash: str) -> str:
        data = f"{canonical_payload_str}||{previous_hash}".encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def log_event(
        cls,
        db: Session,
        request_id: str,
        application_id: str,
        agent_id: str,
        user_id: str,
        action_type: str,
        assurance_level: str,
        decision: str,
        policy_id: str,
        policy_version: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> AuditEventModel:
        sanitized_payload = cls.redact_sensitive_data(payload)
        payload_json = json.dumps(sanitized_payload, sort_keys=True)

        last_event = DBService.get_last_audit_event(db)
        prev_hash = last_event.current_event_hash if last_event else cls.GENESIS_HASH

        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        canonical_str = f"{event_id}|{request_id}|{application_id}|{agent_id}|{user_id}|{action_type}|{assurance_level}|{decision}|{policy_id}|{policy_version}|{event_type}|{payload_json}"
        current_hash = cls.compute_event_hash(canonical_str, prev_hash)

        event_model = AuditEventModel(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            request_id=request_id,
            application_id=application_id,
            agent_id=agent_id,
            user_id=user_id,
            action_type=action_type,
            assurance_level=assurance_level,
            decision=decision,
            policy_id=policy_id,
            policy_version=policy_version,
            event_type=event_type,
            payload_json=payload_json,
            previous_event_hash=prev_hash,
            current_event_hash=current_hash
        )

        return DBService.save_audit_event(db, event_model)

    @classmethod
    def verify_audit_chain(cls, events: List[AuditEventModel]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verifies the cryptographic SHA-256 hash chain of audit records.
        Returns: (is_valid, message, broken_event_id)
        """
        if not events:
            return True, "Audit chain empty (VALID)", None

        expected_prev_hash = cls.GENESIS_HASH

        for event in events:
            if event.previous_event_hash != expected_prev_hash:
                return False, f"Tamper Detected: Event '{event.event_id}' previous_event_hash mismatch (expected '{expected_prev_hash[:10]}...', got '{event.previous_event_hash[:10]}...')", event.event_id

            canonical_str = f"{event.event_id}|{event.request_id}|{event.application_id}|{event.agent_id}|{event.user_id}|{event.action_type}|{event.assurance_level}|{event.decision}|{event.policy_id}|{event.policy_version}|{event.event_type}|{event.payload_json}"
            computed_hash = cls.compute_event_hash(canonical_str, expected_prev_hash)

            if computed_hash != event.current_event_hash:
                return False, f"Tamper Detected: Event '{event.event_id}' content payload or current_event_hash altered!", event.event_id

            expected_prev_hash = event.current_event_hash

        return True, "Audit integrity chain verification successful (AUDIT INTEGRITY: VALID)", None
