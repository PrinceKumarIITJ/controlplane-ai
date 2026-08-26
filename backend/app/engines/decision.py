from typing import Dict, Any, Tuple
from app.schemas.governance import AssuranceLevel, CanonicalDecision, RiskAssessment

class DecisionEngine:
    @staticmethod
    def evaluate_decision(
        assurance_level: AssuranceLevel,
        risk_assessment: RiskAssessment,
        grounding_status: str,
        cost_deviation: float,
        policy: Dict[str, Any]
    ) -> Tuple[CanonicalDecision, bool, str, str]:
        """
        Evaluates canonical decision using sequential precedence rules.
        Returns: (decision, warning, rule_triggered, reason)
        """
        risk_tolerance = policy.get("risk_tolerance", {})
        block_threshold = risk_tolerance.get("composite_risk_block_threshold", 0.65)
        recheck_threshold = risk_tolerance.get("composite_risk_recheck_threshold", 0.40)
        reroute_threshold = risk_tolerance.get("cost_deviation_reroute_threshold", 3.5)

        # Rule 1: Hard Security / Responsibility Violation
        if risk_assessment.responsibility_risk >= 0.80:
            return (
                CanonicalDecision.BLOCK,
                False,
                "HARD_SECURITY_VIOLATION",
                "Action blocked due to responsibility or security violation (Prompt Injection / Secret Exfiltration)."
            )

        # Rule 2: Assurance Level == L3 (Critical Action Floor)
        if assurance_level == AssuranceLevel.L3:
            return (
                CanonicalDecision.HUMAN_REVIEW,
                True,
                "L3_CRITICAL_ACTION_FLOOR",
                "High-impact or irreversible critical action requires mandatory human authorization."
            )

        # Rule 3: High Impact (BI >= 75) AND Insufficient Confidence (DC < 0.60)
        if risk_assessment.business_impact >= 75.0 and risk_assessment.detection_confidence < 0.60:
            return (
                CanonicalDecision.HUMAN_REVIEW,
                True,
                "HIGH_IMPACT_LOW_CONFIDENCE",
                "High business impact combined with insufficient detection confidence requires human authorization."
            )

        # Rule 4: Excessive Cost Deviation
        if cost_deviation >= reroute_threshold:
            return (
                CanonicalDecision.REROUTE,
                True,
                "EXCESSIVE_COST_DEVIATION",
                f"Action cost deviation ({cost_deviation:.1f}x) exceeds threshold ({reroute_threshold}x). Policy triggers model reroute."
            )

        # Rule 5: High Composite Risk
        if risk_assessment.composite_risk >= block_threshold:
            return (
                CanonicalDecision.BLOCK,
                False,
                "HIGH_COMPOSITE_RISK",
                f"Composite risk score ({risk_assessment.composite_risk:.2f}) exceeds policy block threshold ({block_threshold})."
            )

        # Rule 6: Moderate Risk / Contradicted Grounding
        if risk_assessment.composite_risk >= recheck_threshold or grounding_status == "CONTRADICTED":
            return (
                CanonicalDecision.RECHECK,
                True,
                "MODERATE_RISK_RECHECK",
                "Moderate risk score or contradicted grounding status requires AI agent recheck."
            )

        # Rule 7: Default Safe Criteria Satisfied
        return (
            CanonicalDecision.ALLOW,
            False,
            "DEFAULT_SAFE_ALLOW",
            "Action satisfied all safety, responsibility, cost, and impact policy thresholds."
        )
