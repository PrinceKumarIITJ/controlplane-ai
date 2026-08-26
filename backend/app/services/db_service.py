import json
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.domain import (
    PolicyModel, AgentActionModel, DecisionModel,
    ApprovalTokenModel, HumanReviewModel, AuditEventModel
)

class DBService:
    @staticmethod
    def get_policy(db: Session, policy_id: str, version: str) -> Optional[PolicyModel]:
        return db.query(PolicyModel).filter(
            PolicyModel.policy_id == policy_id,
            PolicyModel.version == version,
            PolicyModel.is_active == True
        ).first()

    @staticmethod
    def get_active_policy_by_app(db: Session, application_id: str) -> Optional[PolicyModel]:
        return db.query(PolicyModel).filter(
            PolicyModel.application_id == application_id,
            PolicyModel.is_active == True
        ).order_by(PolicyModel.created_at.desc()).first()

    @staticmethod
    def save_policy(db: Session, policy: PolicyModel) -> PolicyModel:
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def save_action(db: Session, action: AgentActionModel) -> AgentActionModel:
        db.add(action)
        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def get_action(db: Session, action_id: str) -> Optional[AgentActionModel]:
        return db.query(AgentActionModel).filter(AgentActionModel.action_id == action_id).first()

    @staticmethod
    def update_action_status(db: Session, action_id: str, status: str) -> Optional[AgentActionModel]:
        action = db.query(AgentActionModel).filter(AgentActionModel.action_id == action_id).first()
        if action:
            action.status = status
            db.commit()
            db.refresh(action)
        return action

    @staticmethod
    def save_decision(db: Session, decision: DecisionModel) -> DecisionModel:
        db.add(decision)
        db.commit()
        db.refresh(decision)
        return decision

    @staticmethod
    def get_decision(db: Session, decision_id: str) -> Optional[DecisionModel]:
        return db.query(DecisionModel).filter(DecisionModel.decision_id == decision_id).first()

    @staticmethod
    def get_decision_by_action(db: Session, action_id: str) -> Optional[DecisionModel]:
        return db.query(DecisionModel).filter(DecisionModel.action_id == action_id).order_by(DecisionModel.created_at.desc()).first()

    @staticmethod
    def save_token(db: Session, token: ApprovalTokenModel) -> ApprovalTokenModel:
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    @staticmethod
    def get_token_by_nonce(db: Session, nonce: str) -> Optional[ApprovalTokenModel]:
        return db.query(ApprovalTokenModel).filter(ApprovalTokenModel.nonce == nonce).first()

    @staticmethod
    def get_token_by_action(db: Session, action_id: str) -> Optional[ApprovalTokenModel]:
        return db.query(ApprovalTokenModel).filter(ApprovalTokenModel.action_id == action_id, ApprovalTokenModel.status == "ISSUED").first()

    @staticmethod
    def save_review(db: Session, review: HumanReviewModel) -> HumanReviewModel:
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def get_pending_reviews(db: Session) -> List[AgentActionModel]:
        return db.query(AgentActionModel).filter(AgentActionModel.status == "PENDING_REVIEW").order_by(AgentActionModel.created_at.desc()).all()

    @staticmethod
    def get_last_audit_event(db: Session) -> Optional[AuditEventModel]:
        return db.query(AuditEventModel).order_by(AuditEventModel.timestamp.desc()).first()

    @staticmethod
    def save_audit_event(db: Session, event: AuditEventModel) -> AuditEventModel:
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_all_audit_events(db: Session) -> List[AuditEventModel]:
        return db.query(AuditEventModel).order_by(AuditEventModel.timestamp.asc()).all()
