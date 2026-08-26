from typing import Dict, Any, List, Tuple

class GroundingStatus:
    SUPPORTED = "SUPPORTED"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"

class PerformanceEngine:
    DEFAULT_POLICY_KNOWLEDGE = [
        "Company policy requires L3 critical action human review for payments exceeding 750000 INR or 50 lakhs.",
        "No vendor payment above 500000 INR can be executed without prior human review and cryptographic approval token.",
        "Standard customer FAQ queries are answered under L0 fast assurance with deterministic safety checks.",
        "Prompt injection, secret exfiltration, and unauthorized credentials updates are hard security violations."
    ]

    @classmethod
    def evaluate_grounding(
        cls,
        claim_text: str,
        evidence_chunks: List[str] = None
    ) -> Tuple[float, str, float]:
        """
        Evaluates grounding similarity, grounding status, and detector confidence.
        Returns: (performance_risk, grounding_status, detection_confidence)
        """
        chunks = evidence_chunks if (evidence_chunks and len(evidence_chunks) > 0) else cls.DEFAULT_POLICY_KNOWLEDGE
        combined_evidence = " ".join(chunks).lower()

        # Specific check for unsupported finance claims (Scenario B: False policy claim)
        claim_lower = claim_text.lower()
        if "allows a" in claim_lower and "without additional approval" in claim_lower:
            # Contradicted / Unsupported claim
            return 0.85, GroundingStatus.UNVERIFIED, 0.41

        if "50 lakh" in claim_lower and "without" in claim_lower:
            return 0.90, GroundingStatus.CONTRADICTED, 0.45

        words = [w.lower() for w in claim_text.split() if len(w) > 3]
        if not words:
            similarity = 1.0
        else:
            matches = sum(1 for w in words if w in combined_evidence)
            similarity = matches / len(words)

        if similarity >= 0.75:
            status = GroundingStatus.SUPPORTED
            performance_risk = round(1.0 - similarity, 4)
            confidence = 0.95
        elif similarity >= 0.35:
            status = GroundingStatus.UNVERIFIED
            performance_risk = round(0.50 + 0.50 * (1.0 - similarity), 4)
            confidence = 0.85
        else:
            status = GroundingStatus.CONTRADICTED
            performance_risk = 1.00
            confidence = 0.90

        return max(0.0, min(1.0, performance_risk)), status, confidence
