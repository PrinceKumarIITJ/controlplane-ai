from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.audit_service import AuditService
from app.services.db_service import DBService

router = APIRouter(prefix="/audit", tags=["Audit & Integrity"])

@router.get("/events")
def get_audit_events(db: Session = Depends(get_db)):
    events = DBService.get_all_audit_events(db)
    is_valid, msg, broken_id = AuditService.verify_audit_chain(events)
    
    events_data = []
    for e in events:
        events_data.append({
            "event_id": e.event_id,
            "timestamp": e.timestamp,
            "request_id": e.request_id,
            "application_id": e.application_id,
            "agent_id": e.agent_id,
            "user_id": e.user_id,
            "action_type": e.action_type,
            "assurance_level": e.assurance_level,
            "decision": e.decision,
            "policy_id": e.policy_id,
            "policy_version": e.policy_version,
            "event_type": e.event_type,
            "payload_json": e.payload_json,
            "previous_event_hash": e.previous_event_hash,
            "current_event_hash": e.current_event_hash
        })
        
    return {
        "audit_integrity": "VALID" if is_valid else "BROKEN",
        "verification_message": msg,
        "broken_event_id": broken_id,
        "total_events": len(events),
        "events": events_data
    }

@router.get("/verify")
def verify_audit_integrity(db: Session = Depends(get_db)):
    events = DBService.get_all_audit_events(db)
    is_valid, msg, broken_id = AuditService.verify_audit_chain(events)
    return {
        "audit_integrity": "VALID" if is_valid else "BROKEN",
        "message": msg,
        "broken_event_id": broken_id
    }

@router.post("/tamper_test")
def simulate_tampering(db: Session = Depends(get_db)):
    """Simulates unauthorized database tampering on the most recent audit record."""
    last_event = DBService.get_last_audit_event(db)
    if not last_event:
        raise HTTPException(status_code=400, detail="No audit records exist to tamper with.")

    # Alter historical event payload directly in database
    last_event.payload_json = '{"tampered": true, "unauthorized_change": "MODIFIED_DECISION_TO_ALLOW"}'
    db.commit()

    # Run verification immediately
    events = DBService.get_all_audit_events(db)
    is_valid, msg, broken_id = AuditService.verify_audit_chain(events)

    return {
        "status": "TAMPER_SIMULATED",
        "tampered_event_id": last_event.event_id,
        "audit_integrity": "VALID" if is_valid else "BROKEN",
        "verification_message": msg
    }

@router.post("/reset")
def reset_audit_chain(db: Session = Depends(get_db)):
    """Re-computes and restores valid cryptographic SHA-256 hash chain links."""
    events = DBService.get_all_audit_events(db)
    prev_hash = AuditService.GENESIS_HASH
    
    for evt in events:
        evt.previous_event_hash = prev_hash
        canonical_str = f"{evt.event_id}|{evt.request_id}|{evt.application_id}|{evt.agent_id}|{evt.user_id}|{evt.action_type}|{evt.assurance_level}|{evt.decision}|{evt.policy_id}|{evt.policy_version}|{evt.event_type}|{evt.payload_json}"
        evt.current_event_hash = AuditService.compute_event_hash(canonical_str, prev_hash)
        prev_hash = evt.current_event_hash

    db.commit()
    return {"status": "SUCCESS", "message": "Audit chain re-anchored. AUDIT INTEGRITY: VALID"}
