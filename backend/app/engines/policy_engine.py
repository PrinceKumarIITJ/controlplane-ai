import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.db_service import DBService
from app.schemas.governance import AgentAction

class PolicyEngine:
    @staticmethod
    def load_policy(db: Session, application_id: str, policy_id: Optional[str] = None, version: Optional[str] = None) -> Dict[str, Any]:
        if policy_id and version:
            policy_model = DBService.get_policy(db, policy_id, version)
        else:
            policy_model = DBService.get_active_policy_by_app(db, application_id)

        if not policy_model:
            # Fallback default policy if none found in DB
            return {
                "policy_id": policy_id or "DEFAULT_POLICY",
                "version": version or "1.0.0",
                "name": "Default Safety Policy",
                "application_id": application_id,
                "risk_tolerance": {
                    "composite_risk_block_threshold": 0.65,
                    "composite_risk_recheck_threshold": 0.40,
                    "cost_deviation_reroute_threshold": 3.5
                },
                "business_impact_rules": {
                    "l3_threshold": 75.0,
                    "high_impact_confidence_floor": 0.60,
                    "high_risk_action_types": ["PAYMENT", "DELETE_DATA", "UPDATE_CREDENTIALS", "EXECUTE_CODE"],
                    "irreversible_actions_l3": True
                },
                "assurance_thresholds": {
                    "l0_cost_max": 0.05,
                    "l1_composite_risk_max": 0.40
                },
                "weights": {
                    "w_perf": 0.30,
                    "w_cost": 0.20,
                    "w_resp": 0.30,
                    "w_impact": 0.20
                },
                "fail_closed": True
            }

        return json.loads(policy_model.rules_json)
