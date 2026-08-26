from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import AgentActionModel, DecisionModel, AuditEventModel
from app.services.target_service import TargetService
from app.services.audit_service import AuditService
from app.services.db_service import DBService

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/summary")
def get_metrics_summary(db: Session = Depends(get_db)):
    total_actions = db.query(AgentActionModel).count()
    pending_reviews = db.query(AgentActionModel).filter(AgentActionModel.status == "PENDING_REVIEW").count()
    authorized_actions = db.query(AgentActionModel).filter(AgentActionModel.status == "AUTHORIZED").count()
    blocked_actions = db.query(AgentActionModel).filter(AgentActionModel.status == "BLOCKED").count()
    rejected_actions = db.query(AgentActionModel).filter(AgentActionModel.status == "REJECTED").count()
    executed_actions = db.query(AgentActionModel).filter(AgentActionModel.status == "EXECUTED").count()

    events = DBService.get_all_audit_events(db)
    is_valid, msg, broken_id = AuditService.verify_audit_chain(events)

    return {
        "total_interactions": total_actions,
        "pending_human_reviews": pending_reviews,
        "authorized_count": authorized_actions,
        "blocked_count": blocked_actions,
        "rejected_count": rejected_actions,
        "executed_count": executed_actions,
        "mock_target_calls": {
            "payment_api_call_count": TargetService.get_payment_api_call_count(),
            "catalog_api_call_count": TargetService.get_catalog_api_call_count()
        },
        "audit_integrity": "VALID" if is_valid else "BROKEN",
        "audit_verification_message": msg
    }
