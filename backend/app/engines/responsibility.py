import re
from typing import Dict, Any, List, Tuple

class ResponsibilityEngine:
    PII_PATTERNS = [
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "EMAIL", 0.8),
        (r'\b\d{3}-\d{2}-\d{4}\b', "SSN", 1.0),
        (r'\b(?:\d[ -]*?){13,16}\b', "CREDIT_CARD", 1.0),
    ]

    SECRET_PATTERNS = [
        (r'sk-[a-zA-Z0-9]{20,}', "OPENAI_API_KEY", 1.0),
        (r'AKIA[0-9A-Z]{16}', "AWS_ACCESS_KEY", 1.0),
        (r'ghp_[a-zA-Z0-9]{36}', "GITHUB_TOKEN", 1.0),
        (r'bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*', "BEARER_TOKEN", 0.9),
    ]

    INJECTION_PATTERNS = [
        (r'ignore\s+previous\s+instructions', "PROMPT_INJECTION", 1.0),
        (r'system\s+override', "PROMPT_INJECTION", 1.0),
        (r'exfiltrate', "DATA_EXFILTRATION", 1.0),
        (r'drop\s+database', "SQL_INJECTION", 1.0),
        (r'sudo\s+rm\s+-rf', "COMMAND_INJECTION", 1.0),
    ]

    @staticmethod
    def evaluate_responsibility(
        payload_text: str
    ) -> Tuple[float, List[Dict[str, Any]], float]:
        """
        Scans payload text for PII, secrets, and prompt injection patterns.
        Returns: (responsibility_risk, detected_violations, detector_confidence)
        """
        violations = []
        max_risk = 0.0

        # Scan PII
        for pattern, label, severity in ResponsibilityEngine.PII_PATTERNS:
            if re.search(pattern, payload_text, re.IGNORECASE):
                risk = severity * 0.9
                max_risk = max(max_risk, risk)
                violations.append({
                    "category": "PII",
                    "label": label,
                    "severity": severity,
                    "confidence": 0.9
                })

        # Scan Secrets
        for pattern, label, severity in ResponsibilityEngine.SECRET_PATTERNS:
            if re.search(pattern, payload_text, re.IGNORECASE):
                risk = severity * 1.0
                max_risk = max(max_risk, risk)
                violations.append({
                    "category": "SECRET_LEAK",
                    "label": label,
                    "severity": severity,
                    "confidence": 1.0
                })

        # Scan Prompt Injection
        for pattern, label, severity in ResponsibilityEngine.INJECTION_PATTERNS:
            if re.search(pattern, payload_text, re.IGNORECASE):
                risk = severity * 1.0
                max_risk = max(max_risk, risk)
                violations.append({
                    "category": "SECURITY_VIOLATION",
                    "label": label,
                    "severity": severity,
                    "confidence": 1.0
                })

        detector_confidence = 0.95 if violations else 0.90
        return max_risk, violations, detector_confidence
