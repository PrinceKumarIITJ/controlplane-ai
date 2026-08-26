from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.governance import AgentAction, GovernanceDecisionResponse
from app.services.interceptor_service import InterceptorService

router = APIRouter(prefix="/govern", tags=["Governance"])

@router.post("/action", response_model=GovernanceDecisionResponse)
def govern_agent_action(
    action: AgentAction,
    db: Session = Depends(get_db)
):
    try:
        decision_response = InterceptorService.govern_action(db, action)
        return decision_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Governance Pipeline Exception: {str(e)}"
        )
