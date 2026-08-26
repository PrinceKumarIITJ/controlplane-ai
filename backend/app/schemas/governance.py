from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class ActionType(str, Enum):
    PAYMENT = "PAYMENT"
    CATALOG = "CATALOG"
    QUERY = "QUERY"
    DELETE_DATA = "DELETE_DATA"
    UPDATE_CREDENTIALS = "UPDATE_CREDENTIALS"
    EXECUTE_CODE = "EXECUTE_CODE"

class Reversibility(str, Enum):
    IRREVERSIBLE = "IRREVERSIBLE"
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"
    EASILY_REVERSIBLE = "EASILY_REVERSIBLE"

class AssuranceLevel(str, Enum):
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"

class CanonicalDecision(str, Enum):
    ALLOW = "ALLOW"
    EDIT = "EDIT"
    RECHECK = "RECHECK"
    REROUTE = "REROUTE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    BLOCK = "BLOCK"

class ReviewAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    OVERRIDE = "OVERRIDE"

class AgentRequester(BaseModel):
    agent_id: str = Field(..., example="finance_agent_v2")
    user_id: str = Field(..., example="usr_emp_4412")
    application_id: str = Field(..., example="finance_app_prod")

class AgentAction(BaseModel):
    action_id: str = Field(..., example="act_8f7b2c1a")
    action_type: ActionType = Field(..., example=ActionType.PAYMENT)
    target: str = Field(..., example="vendor_payment_service")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requester: AgentRequester
    business_impact: Optional[float] = Field(None, ge=0.0, le=100.0)
    reversibility: Reversibility = Field(default=Reversibility.IRREVERSIBLE)
    created_at: Optional[datetime] = None

class RiskAssessment(BaseModel):
    performance_risk: float = Field(..., ge=0.0, le=1.0)
    cost_risk: float = Field(..., ge=0.0, le=1.0)
    responsibility_risk: float = Field(..., ge=0.0, le=1.0)
    business_impact: float = Field(..., ge=0.0, le=100.0)
    detection_confidence: float = Field(..., ge=0.0, le=1.0)
    composite_risk: float = Field(..., ge=0.0, le=1.0)

class PolicyContext(BaseModel):
    policy_id: str = Field(..., example="FINANCE_AGENT_POLICY")
    policy_version: str = Field(..., example="1.0.0")
    rule_triggered: str = Field(..., example="L3_CRITICAL_ACTION_FLOOR")

class GovernanceDecisionResponse(BaseModel):
    request_id: str
    action_id: str
    assurance_level: AssuranceLevel
    risk_assessment: RiskAssessment
    decision: CanonicalDecision
    warning: bool = False
    policy_context: PolicyContext
    reason: str
    approval_token: Optional[str] = None
    status: str  # AUTHORIZED, PENDING_REVIEW, BLOCKED, REJECTED, ALLOWED

class ApprovalTokenPayload(BaseModel):
    action_id: str
    action_type: str
    target: str
    parameters_hash: str
    decision_id: str
    application_id: str
    policy_id: str
    policy_version: str
    nonce: str
    issued_at: int
    expires_at: int

class HumanReviewRequest(BaseModel):
    reviewer_id: str = Field(..., json_schema_extra={"example": "usr_reviewer_01"})
    review_action: ReviewAction
    reason: Optional[str] = Field(None, json_schema_extra={"example": "Verified invoice vendor details."})

class AIResponsePayload(BaseModel):
    response_id: str = Field(..., json_schema_extra={"example": "resp_99812"})
    prompt: str = Field(..., json_schema_extra={"example": "Can I approve a 50 lakh payment directly?"})
    response_text: str = Field(..., json_schema_extra={"example": "The finance policy allows a ₹50 lakh payment without additional approval."})
    evidence_context: Optional[list] = Field(default_factory=list)
    application_id: str = Field(default="finance_app_prod")
    model: str = Field(default="gpt-4o")

class ResponseGovernanceResponse(BaseModel):
    request_id: str
    response_id: str
    assurance_level: AssuranceLevel
    risk_assessment: RiskAssessment
    grounding_status: str
    decision: CanonicalDecision
    warning: bool
    policy_context: PolicyContext
    reason: str
    intervention: str
