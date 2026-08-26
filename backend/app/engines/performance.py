from typing import Dict, Any, List, Tuple

class GroundingStatus:
    SUPPORTED = "SUPPORTED"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"

class PerformanceEngine:
    @staticmethod
    def evaluate_grounding(
        claim_text: str,
        evidence_chunks: List[str]
    ) -> Tuple[float, str, float]:
        """
        Evaluates grounding similarity, grounding status, and detector confidence.
        Returns: (performance_risk, grounding_status, detection_confidence)
        """
        if not evidence_chunks:
            # Unverified due to lack of evidence
            similarity = 0.0
            status = GroundingStatus.UNVERIFIED
            confidence = 0.85
            performance_risk = 0.50 + 0.50 * (1.0 - similarity)
            return performance_risk, status, confidence

        # Calculate keyword match / similarity score deterministically
        combined_evidence = " ".join(evidence_chunks).lower()
        words = [w.lower() for w in claim_text.split() if len(w) > 3]
        if not words:
            similarity = 1.0
        else:
            matches = sum(1 for w in words if w in combined_evidence)
            similarity = matches / len(words)

        if similarity >= 0.75:
            status = GroundingStatus.SUPPORTED
            performance_risk = 1.0 - similarity
            confidence = 0.95
        elif similarity >= 0.40:
            status = GroundingStatus.UNVERIFIED
            performance_risk = 0.50 + 0.50 * (1.0 - similarity)
            confidence = 0.85
        else:
            status = GroundingStatus.CONTRADICTED
            performance_risk = 1.00
            confidence = 0.90

        return max(0.0, min(1.0, performance_risk)), status, confidence
