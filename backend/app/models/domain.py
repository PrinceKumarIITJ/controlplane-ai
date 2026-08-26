import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, UniqueConstraint, Index, ForeignKey
)
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class PolicyModel(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, default=generate_uuid)
    policy_id = Column(String, nullable=False)
    version = Column(String, nullable=False)
    name = Column(String, nullable=False)
    application_id = Column(String, nullable=False)
    rules_json = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("policy_id", "version", name="uq_policy_version"),
        Index("idx_policies_lookup", "policy_id", "version"),
    )

class AgentActionModel(Base):
    __tablename__ = "agent_actions"

    id = Column(String, primary_key=True, default=generate_uuid)
    action_id = Column(String, unique=True, nullable=False, index=True)
    action_type = Column(String, nullable=False)
    target = Column(String, nullable=False)
    parameters_hash = Column(String, nullable=False)
    parameters_json = Column(Text, nullable=False)
    agent_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    application_id = Column(String, nullable=False)
    business_impact = Column(Float, nullable=False)
    reversibility = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True) # PENDING_REVIEW, AUTHORIZED, REJECTED, BLOCKED, EXECUTED
    created_at = Column(DateTime, default=datetime.utcnow)

class DecisionModel(Base):
    __tablename__ = "decisions"

    id = Column(String, primary_key=True, default=generate_uuid)
    decision_id = Column(String, unique=True, nullable=False, index=True)
    action_id = Column(String, ForeignKey("agent_actions.action_id"), nullable=False, index=True)
    assurance_level = Column(String, nullable=False) # L0, L1, L2, L3
    performance_risk = Column(Float, nullable=False)
    cost_risk = Column(Float, nullable=False)
    responsibility_risk = Column(Float, nullable=False)
    business_impact = Column(Float, nullable=False)
    detection_confidence = Column(Float, nullable=False)
    composite_risk = Column(Float, nullable=False)
    decision = Column(String, nullable=False) # ALLOW, EDIT, RECHECK, REROUTE, HUMAN_REVIEW, BLOCK
    warning = Column(Boolean, default=False)
    policy_id = Column(String, nullable=False)
    policy_version = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    rule_triggered = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_decisions_policy", "policy_id", "policy_version"),
    )

class ApprovalTokenModel(Base):
    __tablename__ = "approval_tokens"

    id = Column(String, primary_key=True, default=generate_uuid)
    token_id = Column(String, unique=True, nullable=False, index=True)
    action_id = Column(String, ForeignKey("agent_actions.action_id"), nullable=False, index=True)
    decision_id = Column(String, ForeignKey("decisions.decision_id"), nullable=False)
    parameters_hash = Column(String, nullable=False)
    signature = Column(String, nullable=False)
    nonce = Column(String, unique=True, nullable=False, index=True)
    policy_id = Column(String, nullable=False)
    policy_version = Column(String, nullable=False)
    issued_at = Column(Integer, nullable=False)
    expires_at = Column(Integer, nullable=False)
    status = Column(String, nullable=False) # ISSUED, CONSUMED, EXPIRED, REVOKED
    consumed_at = Column(DateTime, nullable=True)

class HumanReviewModel(Base):
    __tablename__ = "human_reviews"

    id = Column(String, primary_key=True, default=generate_uuid)
    review_id = Column(String, unique=True, nullable=False, index=True)
    action_id = Column(String, ForeignKey("agent_actions.action_id"), nullable=False, index=True)
    decision_id = Column(String, ForeignKey("decisions.decision_id"), nullable=False)
    reviewer_id = Column(String, nullable=False)
    review_action = Column(String, nullable=False) # APPROVE, REJECT, OVERRIDE
    reason = Column(Text, nullable=True)
    policy_id = Column(String, nullable=False)
    policy_version = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, unique=True, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    request_id = Column(String, nullable=False)
    application_id = Column(String, nullable=False)
    agent_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    assurance_level = Column(String, nullable=False)
    decision = Column(String, nullable=False)
    policy_id = Column(String, nullable=False)
    policy_version = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload_json = Column(Text, nullable=False)
    previous_event_hash = Column(String, nullable=False)
    current_event_hash = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_audit_policy", "policy_id", "policy_version"),
    )
