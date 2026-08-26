from typing import Dict, Any
from app.schemas.governance import RiskAssessment

class RiskEngine:
    @staticmethod
    def calculate_composite_risk(
        performance_risk: float,
        cost_risk: float,
        responsibility_risk: float,
        business_impact: float,
        detection_confidence: float,
        policy: Dict[str, Any]
    ) -> RiskAssessment:
        """
        Aggregates individual risks into a Composite Risk score (0.0 - 1.0).
        CR = w_perf * R_perf + w_cost * R_cost + w_resp * R_resp + w_impact * (BI / 100)
        """
        weights = policy.get("weights", {})
        w_perf = weights.get("w_perf", 0.30)
        w_cost = weights.get("w_cost", 0.20)
        w_resp = weights.get("w_resp", 0.30)
        w_impact = weights.get("w_impact", 0.20)

        composite_risk = (
            w_perf * performance_risk +
            w_cost * cost_risk +
            w_resp * responsibility_risk +
            w_impact * (business_impact / 100.0)
        )

        composite_risk = max(0.0, min(1.0, round(composite_risk, 4)))

        return RiskAssessment(
            performance_risk=round(performance_risk, 4),
            cost_risk=round(cost_risk, 4),
            responsibility_risk=round(responsibility_risk, 4),
            business_impact=round(business_impact, 2),
            detection_confidence=round(detection_confidence, 4),
            composite_risk=composite_risk
        )
