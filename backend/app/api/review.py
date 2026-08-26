from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.governance import HumanReviewRequest
from app.services.review_service import ReviewService
from app.services.db_service import DBService

router = APIRouter(prefix="/review", tags=["Human Review"])

@router.get("/pending")
def list_pending_reviews(db: Session = Depends(get_db)):
    pending_actions = DBService.get_pending_reviews(db)
    result = []
    for act in pending_actions:
        dec = DBService.get_decision_by_action(db, act.action_id)
        result.append({
            "action_id": act.action_id,
            "action_type": act.action_type,
            "target": act.target,
            "parameters": act.parameters_json,
            "agent_id": act.agent_id,
            "user_id": act.user_id,
            "application_id": act.application_id,
            "business_impact": act.business_impact,
            "reversibility": act.reversibility,
            "status": act.status,
            "created_at": act.created_at,
            "decision_context": {
                "decision_id": dec.decision_id if dec else None,
                "assurance_level": dec.assurance_level if dec else "L3",
                "composite_risk": dec.composite_risk if dec else 0.0,
                "reason": dec.reason if dec else "L3 Critical Action Floor",
                "rule_triggered": dec.rule_triggered if dec else "L3_CRITICAL_ACTION_FLOOR"
            }
        })
    return result

@router.post("/{action_id}")
def process_review(
    action_id: str,
    review_req: HumanReviewRequest,
    db: Session = Depends(get_db)
):
    success, msg, token_str, action_dict = ReviewService.process_human_review(db, action_id, review_req)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    
    return {
        "status": "SUCCESS",
        "message": msg,
        "action": action_dict,
        "approval_token": token_str
    }
