# ControlPlane.ai — 3-Minute Hero Demonstration Script

This guide provides a step-by-step 3 to 5 minute presentation script for evaluators and presenters demonstrating the ControlPlane.ai real-time AI assurance control plane.

---

## Pre-Demo Setup

1. **Start Backend Server**:
   ```bash
   python backend/app/main.py
   ```
2. **Start Frontend Control Center**:
   ```bash
   cd frontend && npm run dev
   ```
3. **Open Browser**: Navigate to `http://localhost:3000`.

---

## 16-Step Recommended Presentation Sequence

### Step 1: Open Command Center
* **WHAT TO CLICK**: Click **Command Center** tab on the left sidebar.
* **WHAT TO SAY**: *"Welcome to ControlPlane.ai. This is an inline AI assurance control plane that governs AI agent responses and tool actions before execution."*
* **WHAT SHOULD HAPPEN**: The real-time metrics dashboard loads showing interaction counters and mock target system counters.
* **WHAT RESULT PROVES THE CONCEPT**: Observability dashboard initializes cleanly with active counters.

---

### Step 2: Verify Initial Cryptographic Audit Hash Chain
* **WHAT TO CLICK**: Look at the bottom-left sidebar status badge.
* **WHAT TO SAY**: *"Every decision and intervention is cryptographically chained using SHA-256 hashes ($H_n = \text{SHA256}(P_n \parallel H_{n-1})$). As you can see, audit integrity is currently VALID."*
* **WHAT SHOULD HAPPEN**: Green badge displays **`AUDIT INTEGRITY: VALID`**.
* **WHAT RESULT PROVES THE CONCEPT**: Establishes baseline cryptographic ledger integrity.

---

### Step 3: Run Scenario A — Safe FAQ Request (Flow A & Flow B)
* **WHAT TO CLICK**: Navigate to **Live Hero Interceptor** tab and click **"SCENARIO A — SAFE RESPONSE / QUERY"**.
* **WHAT TO SAY**: *"First, we test a low-risk, grounded FAQ request. ControlPlane evaluates this query in real-time."*
* **WHAT SHOULD HAPPEN**: Pipeline assigns **L0 Fast Assurance** and decision **ALLOW**. An action-bound HMAC token is issued.
* **WHAT RESULT PROVES THE CONCEPT**: Catalog target call succeeds with `HTTP 200 OK`, and **`CATALOG TARGET API CALLS: 1`**.

---

### Step 4: Run Scenario B — Unsupported AI Claim (Flow A Intervention)
* **WHAT TO CLICK**: Click **"SCENARIO B — UNSUPPORTED AI RESPONSE (FLOW A)"**.
* **WHAT TO SAY**: *"Next, we test Flow A Response Governance. An AI model hallucinates a false financial payment policy without evidence."*
* **WHAT SHOULD HAPPEN**: Performance Engine detects status **UNVERIFIED** and triggers decision **RECHECK**.
* **WHAT RESULT PROVES THE CONCEPT**: Response is intercepted before reaching the user; **`TARGET API CALLS: 0`**.

---

### Step 5: Run Scenario C — High-Impact Financial Payment (Human Rejection Path)
* **WHAT TO CLICK**: Click **"SCENARIO C — HIGH IMPACT PAYMENT REJECTED"**.
* **WHAT TO SAY**: *"Now we test Flow B Action Governance for a ₹50 Lakh vendor payment ($BI = 87 \ge 75$)."*
* **WHAT SHOULD HAPPEN**: Business Impact Engine assigns **L3 Critical Action Floor**, forcing decision **HUMAN_REVIEW**. Approval token is withheld (`null`).
* **WHAT RESULT PROVES THE CONCEPT**: Direct attempt to call payment target returns `HTTP 403 Forbidden`; **`PAYMENT TARGET API CALLS: 0`**.

---

### Step 6: Review Pending Human Review Queue
* **WHAT TO CLICK**: Click **Human Review Queue** tab on sidebar.
* **WHAT TO SAY**: *"ControlPlane holds all L3 critical actions in a pending authorization queue until explicit human reviewer action."*
* **WHAT SHOULD HAPPEN**: The ₹50L payment action appears in the queue with full explainable risk breakdown.
* **WHAT RESULT PROVES THE CONCEPT**: Human-in-the-loop authorization queue operates cleanly.

---

### Step 7 & 8: Reject Action & Verify Zero Target Calls
* **WHAT TO CLICK**: Click **"REJECT ACTION"**.
* **WHAT TO SAY**: *"The compliance officer rejects the unauthorized payment."*
* **WHAT SHOULD HAPPEN**: Action is marked `REJECTED`, and zero tokens are issued.
* **WHAT RESULT PROVES THE CONCEPT**: Switch to Command Center; **`PAYMENT TARGET API CALLS: 0`** remains strictly zero.

---

### Step 9 & 10: Run Scenario D — High-Impact Payment (Human Approval Path)
* **WHAT TO CLICK**: Switch back to **Live Hero Interceptor** tab and click **"SCENARIO D — HIGH IMPACT PAYMENT APPROVED"**.
* **WHAT TO SAY**: *"Now we demonstrate valid human approval for the same high-impact payment."*
* **WHAT SHOULD HAPPEN**: The compliance officer approves the transaction after invoice verification.
* **WHAT RESULT PROVES THE CONCEPT**: ControlPlane generates a short-lived, action-bound HMAC-SHA256 Approval Token.

---

### Step 11 & 12: Execute Target Action with Valid Token
* **WHAT TO CLICK**: Observe the Target System Execution panel output.
* **WHAT TO SAY**: *"The Action Guard verifies token HMAC signature, canonical payload hash, and single-use nonce."*
* **WHAT SHOULD HAPPEN**: Target payment system accepts the authorized request with `HTTP 200 OK`.
* **WHAT RESULT PROVES THE CONCEPT**: Target counter increments to **`PAYMENT TARGET API CALLS: 1`**.

---

### Step 13 & 14: Run Scenario E — Malicious Injection & Secret Leak Attack
* **WHAT TO CLICK**: Click **"SCENARIO E — MALICIOUS RESPONSIBILITY VIOLATION"**.
* **WHAT TO SAY**: *"Finally, an attacker attempts a prompt injection to exfiltrate AWS API keys."*
* **WHAT SHOULD HAPPEN**: Responsibility Engine detects Tier 1 (Secret Leak) & Tier 2 (Prompt Injection) violations ($R_{resp} = 1.0$), triggering decision **BLOCK**.
* **WHAT RESULT PROVES THE CONCEPT**: Request is immediately blocked; **`TARGET API CALLS: 0`**.

---

### Step 15 & 16: Demonstrate Cryptographic Audit Chain Tamper Verification & Reset
* **WHAT TO CLICK**: Navigate to **Audit & Integrity** tab, click **"Simulate Tampering"**, observe badge, then click **"Reset Audit Integrity"**.
* **WHAT TO SAY**: *"ControlPlane guarantees audit trail immutability. If a database record is tampered with, the SHA-256 hash chain immediately breaks."*
* **WHAT SHOULD HAPPEN**: Badge instantly turns red (**`AUDIT INTEGRITY: BROKEN`**). Clicking reset restores valid state (**`AUDIT INTEGRITY: VALID`**).
* **WHAT RESULT PROVES THE CONCEPT**: Cryptographic SHA-256 audit ledger guarantees tamper-evident compliance recording.
