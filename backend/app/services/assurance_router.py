from typing import Dict, Any
from app.schemas.governance import AgentAction, AssuranceLevel, Reversibility, ActionType

class AssuranceRouter:
    @staticmethod
    def determine_assurance_level(
        action: AgentAction,
        business_impact_score: float,
        policy: Dict[str, Any]
    ) -> AssuranceLevel:
        bi_rules = policy.get("business_impact_rules", {})
        l3_threshold = bi_rules.get("l3_threshold", 75.0)
        high_risk_types = bi_rules.get("high_risk_action_types", ["PAYMENT", "DELETE_DATA", "UPDATE_CREDENTIALS", "EXECUTE_CODE"])
        irreversible_l3 = bi_rules.get("irreversible_actions_l3", True)

        # L3 Critical Action Assurance Floor Trigger Check
        is_high_impact = business_impact_score >= l3_threshold
        is_irreversible = (action.reversibility == Reversibility.IRREVERSIBLE) and irreversible_l3
        is_high_risk_action = action.action_type.value in high_risk_types

        if is_high_impact or is_irreversible or is_high_risk_action:
            return AssuranceLevel.L3

        # L2 Deep Assurance Check (For moderate-high uncertainty or complex parameters)
        if business_impact_score >= 40.0 or len(str(action.parameters)) > 500:
            return AssuranceLevel.L2

        # L1 Standard Assurance Check
        if business_impact_score >= 15.0 or action.action_type != ActionType.CATALOG:
            return AssuranceLevel.L1

        # Default L0 Fast Assurance
        return AssuranceLevel.L0
