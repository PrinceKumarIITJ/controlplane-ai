from fastapi import APIRouter, Header, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.core.database import get_db
from app.services.action_guard import ActionGuard
from app.services.target_service import TargetService

router = APIRouter(prefix="/mock", tags=["Mock Target Systems"])

@router.post("/catalog")
def mock_catalog_endpoint(
    body: Dict[str, Any],
    response: Response,
    x_controlplane_approval_token: Optional[str] = Header(None, alias="X-ControlPlane-Approval-Token"),
    db: Session = Depends(get_db)
):
    action_id = body.get("action_id", "")
    parameters = body.get("parameters", {})

    is_valid, http_code, message, inc = ActionGuard.validate_and_consume_token(
        db=db,
        token_str=x_controlplane_approval_token,
        expected_action_id=action_id,
        expected_target="catalog_faq_service",
        request_parameters=parameters
    )

    if not is_valid:
        response.status_code = http_code
        return {
            "status": "DENIED",
            "message": message,
            "target_api_calls": TargetService.get_catalog_api_call_count()
        }

    exec_result = TargetService.execute_mock_catalog(parameters)
    response.status_code = status.HTTP_200_OK
    return exec_result

@router.post("/payment")
def mock_payment_endpoint(
    body: Dict[str, Any],
    response: Response,
    x_controlplane_approval_token: Optional[str] = Header(None, alias="X-ControlPlane-Approval-Token"),
    db: Session = Depends(get_db)
):
    action_id = body.get("action_id", "")
    parameters = body.get("parameters", {})

    is_valid, http_code, message, inc = ActionGuard.validate_and_consume_token(
        db=db,
        token_str=x_controlplane_approval_token,
        expected_action_id=action_id,
        expected_target="vendor_payment_service",
        request_parameters=parameters
    )

    if not is_valid:
        response.status_code = http_code
        return {
            "status": "DENIED",
            "message": message,
            "target_api_calls": TargetService.get_payment_api_call_count()
        }

    exec_result = TargetService.execute_mock_payment(parameters)
    response.status_code = status.HTTP_200_OK
    return exec_result

@router.get("/stats")
def get_mock_stats():
    return {
        "payment_api_call_count": TargetService.get_payment_api_call_count(),
        "catalog_api_call_count": TargetService.get_catalog_api_call_count()
    }

@router.post("/reset")
def reset_mock_stats():
    TargetService.reset_counters()
    return {"status": "SUCCESS", "message": "Mock target invocation counters reset to 0."}
