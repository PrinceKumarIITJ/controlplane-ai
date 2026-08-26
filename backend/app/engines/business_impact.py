from typing import Dict, Any
from app.schemas.governance import AgentAction, Reversibility, ActionType

class BusinessImpactEngine:
    @staticmethod
    def calculate_impact(action: AgentAction) -> float:
        """
        Calculates normalized Business Impact score (0-100) using 4 explainable components:
        BI = 0.40 * Financial + 0.25 * Reversibility + 0.20 * DataSensitivity + 0.15 * ExternalImpact
        """
        # If action provides explicit client-side business_impact override, use it if higher
        explicit_impact = action.business_impact or 0.0

        # 1. Financial Impact (0-100)
        params = action.parameters or {}
        amount = float(params.get("amount", 0.0))
        financial_impact = min(100.0, amount / 50000.0)

        # 2. Reversibility (0-100)
        if action.reversibility == Reversibility.IRREVERSIBLE:
            reversibility_score = 100.0
        elif action.reversibility == Reversibility.PARTIALLY_REVERSIBLE:
            reversibility_score = 50.0
        else:
            reversibility_score = 0.0

        # 3. Data Sensitivity (0-100)
        if action.action_type in [ActionType.UPDATE_CREDENTIALS, ActionType.DELETE_DATA]:
            data_sensitivity = 100.0
        elif action.action_type == ActionType.PAYMENT:
            data_sensitivity = 50.0
        elif action.action_type == ActionType.QUERY:
            data_sensitivity = 30.0
        else:
            data_sensitivity = 0.0

        # 4. External Impact (0-100)
        if action.action_type == ActionType.PAYMENT:
            external_impact = 80.0
        elif action.action_type in [ActionType.DELETE_DATA, ActionType.EXECUTE_CODE]:
            external_impact = 100.0
        elif action.action_type == ActionType.CATALOG:
            external_impact = 10.0
        else:
            external_impact = 30.0

        computed_bi = (
            0.40 * financial_impact +
            0.25 * reversibility_score +
            0.20 * data_sensitivity +
            0.15 * external_impact
        )

        final_bi = max(explicit_impact, computed_bi)
        return min(100.0, max(0.0, round(final_bi, 2)))
