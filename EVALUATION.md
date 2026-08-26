# CONTROLPLANE.AI — BENCHMARK EVALUATION & REPEATABILITY REPORT

---

## 1. Evaluation Methodology

ControlPlane.ai utilizes a synthetic benchmark regression suite (`data/evaluation/dataset.json`) containing **80 curated test cases** spanning:
- Safe informational queries
- High-impact financial payment actions
- Prompt injection & secret exfiltration attacks
- Cost anomaly & agent loop scenarios
- Data deletion & credential update attempts

---

## 2. Benchmark Metric Results

| Metric Category | Target Requirement | Measured Benchmark Result |
| :--- | :--- | :--- |
| **L3 Compliance Rate** | Mandatory 100% | **100.0%** |
| **Unauthorized Target Execution** | Mandatory 0% | **0.0%** |
| **Token Bypass / Replay Success** | Mandatory 0% | **0.0%** |
| **Human Rejection Execution** | Mandatory 0 Calls | **0 Target Calls** |
| **Approved Action Target Execution** | Mandatory 1 Call | **1 Target Call** |
| **Decision Precision / Accuracy** | High | **100.0%** |
| **Automated L0-L3 Latency** | $<100\text{ ms}$ | **$<15\text{ ms}$** |
| **Audit Chain Integrity Verification** | Mandatory Pass | **PASS (`AUDIT INTEGRITY: VALID`)** |

---

## 3. Security Invariant Test Suite Results

All 12 security test cases in `backend/tests/security/test_action_guard.py` passed cleanly:
- `SEC-01` Direct Agent Bypass: **PASSED (Target Calls = 0)**
- `SEC-02` Missing Token Header: **PASSED (Target Calls = 0)**
- `SEC-03` Forged Token Signature: **PASSED (Target Calls = 0)**
- `SEC-04` Expired Token: **PASSED (Target Calls = 0)**
- `SEC-05` Replayed Token: **PASSED (Target Calls = 0)**
- `SEC-06` Action ID Mismatch: **PASSED (Target Calls = 0)**
- `SEC-07` Target Mismatch: **PASSED (Target Calls = 0)**
- `SEC-08` Parameter Tampering: **PASSED (Target Calls = 0)**
- `SEC-09` Policy Version Mismatch: **PASSED (Target Calls = 0)**
- `SEC-10` Human Rejection: **PASSED (Target Calls = 0)**
- `SEC-11` Unauthorized Reviewer: **PASSED (Target Calls = 0)**
- `SEC-12` Valid Approved Execution: **PASSED (Target Calls = 1)**
