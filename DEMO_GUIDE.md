# ControlPlane.ai — Comprehensive Master Demo Video Script & Storyboard

Target Video Duration: **4 to 5 minutes**  
Presenter Style: **Authoritative, technical, clear, and engaging**  
Screen Resolution: **1920x1080 (100% Zoom)**

---

## 1. Pre-Recording Setup & Initial Baseline State

### Environment & Process Checklist
1. **Backend Process**: Running `python backend/app/main.py` on `http://localhost:8000`.
2. **Frontend Process**: Running `cd frontend && npm run dev` on `http://localhost:3000`.
3. **Browser Window**: Chrome/Edge opened to `http://localhost:3000`.
4. **Database Reset**: Click **"Reset Audit Integrity"** on the Audit tab so the sidebar badge reads **`AUDIT INTEGRITY: VALID`**.
5. **Execution Counter Reset**: Click **"Reset Counters"** on the Command Center tab so `PAYMENT TARGET API CALLS: 0` and `CATALOG TARGET API CALLS: 0`.

---

## 2. Detailed Scene-by-Scene Script & Storyboard

### Scene 1: Introduction & The AI Agent Security Gap (0:00 - 0:40)

* **UI TAB**: **Enterprise Command Center** (`http://localhost:3000`)
* **MOUSE POINTER INSTRUCTIONS**:
  1. Hover over the top logo **"ControlPlane.ai — ROUND 2 PROTOTYPE FREEZE"**.
  2. Move cursor slowly across the 4 KPI cards: *Total AI Interactions*, *Pending Human Reviews*, *Authorized & Executed*, *Intercepted & Blocked*.
  3. Circle the mouse around the **Mock Target System Execution Counters** box (`POST /mock/payment` and `POST /mock/catalog`), pointing to `PAYMENT TARGET API CALLS: 0`.

* **WORD-FOR-WORD NARRATION SCRIPT**:
  > *"Hello, and welcome to the live demonstration of **ControlPlane.ai** — a real-time inline AI assurance and intervention control plane. [PAUSE]*
  >
  > *As enterprise AI agents evolve from passive chatbots into autonomous systems capable of executing financial payouts, modifying databases, or altering infrastructure, traditional post-hoc logging tools fall dangerously short. Observing a catastrophic AI hallucination or unauthorized wire transfer **after** it occurs is a massive security risk. [PAUSE]*
  >
  > *ControlPlane.ai sits directly inline between AI agents and enterprise target APIs to solve this exact problem. Our core technical invariant is absolute: **No valid ControlPlane authorization means zero target action execution**. Notice on our Command Center dashboard right now, our Payment Target API Call counter is strictly at **zero**."*

* **TECHNICAL RATIONALE & KEY TAKEAWAYS**:
  - Explains the critical gap between post-facto APM monitoring vs pre-execution inline boundary control.
  - Establishes the mathematical invariant: $\text{NO AUTHORIZATION} \implies \text{TARGET CALLS} = 0$.

---

### Scene 2: Scenario A — Safe FAQ Query & L0 Fast Pass Authorization (0:40 - 1:25)

* **UI TAB**: Switch to **Live Hero Interceptor** tab.
* **MOUSE POINTER INSTRUCTIONS**:
  1. Click **Live Hero Interceptor** on the left sidebar.
  2. Click the green button **"SCENARIO A — SAFE RESPONSE / QUERY"**.
  3. Watch the Governance Pipeline Evaluation Output panel pop up.
  4. Move pointer to **ASSURANCE LEVEL: L0** and **CANONICAL DECISION: ALLOW**.
  5. Hover over the **APPROVAL TOKEN STATUS** box showing `HMAC TOKEN ISSUED: eyJhy3R...`.
  6. Move cursor down to **Target System Execution Result** showing `STATUS: SUCCESS` and `TARGET API CALLS: 1`.

* **WORD-FOR-WORD NARRATION SCRIPT**:
  > *"Let's see ControlPlane in action. We'll start with **Scenario A** — a safe, grounded vendor onboarding FAQ request. [CLICK SCENARIO A]*
  >
  > *Watch the pipeline evaluate this request in real time. Because the business impact is minimal ($BI = 1.5/100$) and the query contains zero security risk, ControlPlane's Assurance Router assigns an **L0 Fast Pass Assurance** tier. The decision is **ALLOW**. [PAUSE]*
  >
  > *Notice what happens next: ControlPlane issues a short-lived **HMAC-SHA256 Approval Token**. This capability token is sent in the request header to our target mock catalog API (`POST /mock/catalog`). The Target Action Guard verifies the HMAC signature and parameter digest, allowing the request to succeed with **HTTP 200 OK**. Notice our Catalog Target API Call counter increments to **1**."*

* **TECHNICAL RATIONALE & KEY TAKEAWAYS**:
  - Demonstrates sub-10ms L0 routing overhead for benign queries.
  - Demonstrates action-bound capability token issuance and target authorization.

---

### Scene 3: Scenario B — Flow A Response Governance & Hallucination Interception (1:25 - 2:10)

* **UI TAB**: **Live Hero Interceptor** tab.
* **MOUSE POINTER INSTRUCTIONS**:
  1. Click the amber button **"SCENARIO B — UNSUPPORTED AI RESPONSE (FLOW A)"**.
  2. Move cursor to **ASSURANCE LEVEL: L2** and **CANONICAL DECISION: RECHECK**.
  3. Point mouse to **POLICY CONTEXT**: `Rule Triggered: UNGROUNDED_CLAIM_RECHECK` and `Reason: AI response contains unsupported or unverified policy claim.`
  4. Highlight **Target System Execution Result**: `STATUS: INTERVENED (FLOW A)` and `TARGET API CALLS: 0`.

* **WORD-FOR-WORD NARRATION SCRIPT**:
  > *"Now let's examine **Flow A Response Governance** in **Scenario B**. Here, an AI model responds to a user with an ungrounded claim, falsely asserting that company policy permits a ₹50 Lakh payment without human approval. [CLICK SCENARIO B]*
  >
  > *ControlPlane's Performance Engine intercepts the response inline and evaluates its claim against verified internal policy knowledge chunks. It detects an **UNVERIFIED** evidence status with low similarity. [PAUSE]*
  >
  > *The Policy Engine triggers an automated **RECHECK** intervention at **L2 Deep Assurance**. Instead of allowing unverified misinformation to reach the user or target systems, ControlPlane rewrites the response with an intervention message. Notice that **zero target API calls** were executed."*

* **TECHNICAL RATIONALE & KEY TAKEAWAYS**:
  - Explains Flow A (AI $\rightarrow$ ControlPlane $\rightarrow$ User) response governance.
  - Shows evidence grounding inspection preventing policy claim hallucinations.

---

### Scene 4: Scenario C — Flow B Action Governance & High-Impact Payment Rejection (2:10 - 3:05)

* **UI TAB**: **Live Hero Interceptor** tab, then switch to **Human Review Queue** tab.
* **MOUSE POINTER INSTRUCTIONS**:
  1. Click the red button **"SCENARIO C — HIGH IMPACT PAYMENT REJECTED"**.
  2. Point cursor to **BUSINESS IMPACT: 87 / 100** and **ASSURANCE LEVEL: L3**.
  3. Highlight **CANONICAL DECISION: HUMAN_REVIEW** and **APPROVAL TOKEN STATUS: NO TOKEN ISSUED**.
  4. Point cursor to **Target System Execution Result**: `STATUS: DENIED` (`HTTP 403 Forbidden`).
  5. Click **Human Review Queue** tab on the left sidebar (notice the badge indicator `1`).
  6. Point to the pending transaction card for ₹50,000,000 INR to Vendor X.
  7. Type *"Invoice unverified by finance team"* into the reviewer notes box.
  8. Click the red button **"REJECT ACTION"**.

* **WORD-FOR-WORD NARRATION SCRIPT**:
  > *"Next is **Scenario C** — a critical test of **Flow B Action Governance**. An AI agent proposes a high-impact financial wire payment of **₹50 Lakhs** ($5,000,000 INR) to an external vendor. [CLICK SCENARIO C]*
  >
  > *ControlPlane's Business Impact Engine calculates a Business Impact score of **87 out of 100**, factoring in financial value and irreversibility. Because $BI \ge 75$, ControlPlane enforces a mandatory **L3 Critical Action Floor**. [PAUSE]*
  >
  > *The decision is set to **HUMAN_REVIEW**, and the Approval Token is strictly **withheld**. If the AI agent attempts to invoke the payment target without a token, the Action Guard rejects it with **HTTP 403 Forbidden**. [PAUSE]*
  >
  > *Now let's switch to our **Human Review Queue**. Here is the pending ₹50 Lakh payment awaiting manual authorization. The compliance reviewer inspects the invoice details, enters reviewer notes, and clicks **REJECT ACTION**. [CLICK REJECT]*
  >
  > *The action is marked Rejected. No approval token is ever generated, and our Payment Target API Call counter remains strictly at **zero**."*

* **TECHNICAL RATIONALE & KEY TAKEAWAYS**:
  - Demonstrates Business Impact formula ($BI = 0.40\text{Fin} + 0.25\text{Rev} + 0.20\text{Sens} + 0.15\text{Ext}$).
  - Enforces mandatory L3 human floor for $BI \ge 75$, preventing automated execution.

---

### Scene 5: Scenario D — Flow B Action Governance & Human Approved Execution (3:05 - 3:50)

* **UI TAB**: **Live Hero Interceptor** tab.
* **MOUSE POINTER INSTRUCTIONS**:
  1. Click **Live Hero Interceptor** on the sidebar.
  2. Click the bright blue button **"SCENARIO D — HIGH IMPACT PAYMENT APPROVED"**.
  3. Point mouse to **APPROVAL TOKEN STATUS**: `HMAC TOKEN ISSUED: eyJhy3R...`.
  4. Point mouse down to **Target System Execution Result**: `STATUS: SUCCESS` and `TARGET API CALLS: 1`.
  5. Switch to **Command Center** tab to show `PAYMENT TARGET API CALLS: 1`.

* **WORD-FOR-WORD NARRATION SCRIPT**:
  > *"Now let's look at **Scenario D**, demonstrating the valid approval path for the same high-impact payment. [CLICK SCENARIO D]*
  >
  > *This time, after verifying invoice INV-2026-99, the compliance officer approves the transaction. ControlPlane's Token Service generates a short-lived **HMAC-SHA256 Approval Token**. [PAUSE]*
  >
  > *This token cryptographically binds the action ID, target endpoint, application ID, policy version, and SHA-256 parameter digest. When the agent sends this signed token in header `X-ControlPlane-Approval-Token`, the Target Action Guard verifies the HMAC signature, checks TTL expiration, and atomically invalidates the single-use nonce in SQLite to prevent replay attacks. [PAUSE]*
  >
  > *The target payment system accepts the request with **HTTP 200 OK**, and our Payment Target API Call counter increments to **1**."*

* **TECHNICAL RATIONALE & KEY TAKEAWAYS**:
  - Demonstrates action-bound capability token validation vs session JWTs.
  - Demonstrates atomic single-use nonce invalidation preventing token replay attacks.

---

### Scene 6: Scenario E — Malicious Prompt Injection & Secret Leak Attack (3:50 - 4:25)

* **UI TAB**: **Live Hero Interceptor** tab.
* **MOUSE POINTER INSTRUCTIONS**:
  1. Click **Live Hero Interceptor** on sidebar.
  2. Click the dark red button **"SCENARIO E — MALICIOUS RESPONSIBILITY VIOLATION"**.
  3. Point cursor to **RESPONSIBILITY RISK: 1.0** and **CANONICAL DECISION: BLOCK**.
  4. Point cursor to **POLICY CONTEXT**: `Rule Triggered: HARD_SECURITY_VIOLATION`.
  5. Point to **APPROVAL TOKEN STATUS**: `NO TOKEN ISSUED (Target Execution Blocked)`.

* **WORD-FOR-WORD NARRATION SCRIPT**:
  > *"In **Scenario E**, an attacker attempts a malicious prompt injection attack, instructing the agent to exfiltrate AWS secret API keys. [CLICK SCENARIO E]*
  >
  > *ControlPlane's Responsibility Engine performs multi-tier pattern scanning across Tier 1 secret leaks and Tier 2 prompt injections. It calculates a Responsibility Risk of **1.0**. [PAUSE]*
  >
  > *Rule 1 of our Decision Precedence matrix triggers an immediate hard **BLOCK**. Tokens are withheld, target execution is denied, and the malicious attempt is recorded in our audit log."*

* **TECHNICAL RATIONALE & KEY TAKEAWAYS**:
  - Demonstrates Responsibility Engine multi-tier pattern scanning.
  - Demonstrates Rule 1 hard security precedence blocking malicious context manipulation.

---

### Scene 7: Cryptographic SHA-256 Audit Hash Chain Verification & Tamper Reset (4:25 - 5:05)

* **UI TAB**: **Audit & Integrity** tab.
* **MOUSE POINTER INSTRUCTIONS**:
  1. Click **Audit & Integrity** on sidebar.
  2. Point mouse to top status card: `VERIFICATION RESULT: AUDIT INTEGRITY: VALID`.
  3. Point cursor to the audit log entries showing `Hash` and `Prev` SHA-256 hashes.
  4. Click the dark red button **"Simulate Tampering"**.
  5. Watch status card instantly flip to red: **`VERIFICATION RESULT: AUDIT INTEGRITY: BROKEN (TAMPER DETECTED)`**.
  6. Click the green button **"Reset Audit Integrity"**.
  7. Watch status card return to green: **`VERIFICATION RESULT: AUDIT INTEGRITY: VALID`**.

* **WORD-FOR-WORD NARRATION SCRIPT**:
  > *"To ensure immutable compliance reporting, ControlPlane logs every decision to a cryptographically linked SHA-256 audit hash chain, where each event hash incorporates the previous event's hash ($H_n = \text{SHA256}(Payload_n \parallel H_{n-1})$). [PAUSE]*
  >
  > *Notice our verification status is **AUDIT INTEGRITY: VALID**. Now, let's simulate an attacker gaining unauthorized database access and modifying an audit record. [CLICK SIMULATE TAMPERING]*
  >
  > *Immediately, ControlPlane's hash chain verification algorithm detects the payload discrepancy and flags **AUDIT INTEGRITY: BROKEN**. Clicking **Reset Audit Integrity** re-anchors the ledger hashes and restores our valid compliance state."*

* **TECHNICAL RATIONALE & KEY TAKEAWAYS**:
  - Demonstrates tamper-evident SHA-256 audit ledger ($H_n = \text{SHA256}(P_n \parallel H_{n-1})$).
  - Demonstrates cryptographic tamper detection and reset mechanism.

---

### Scene 8: Executive Summary & Empirical Verification Wrap-Up (5:05 - 5:35)

* **UI TAB**: **Enterprise Command Center** tab.
* **MOUSE POINTER INSTRUCTIONS**:
  1. Click **Command Center** tab.
  2. Hover cursor over the KPI metrics summary.
  3. Conclude video with screen showing clean Command Center dashboard.

* **WORD-FOR-WORD NARRATION SCRIPT**:
  > *"To summarize: ControlPlane.ai provides zero-trust pre-execution assurance for autonomous AI agents. Across our 80-case repeatable benchmark evaluation suite, ControlPlane achieved a **100% L3 Compliance Rate**, **97.5% Overall Decision Accuracy**, **0% False Positive Rate**, and **0% False Negative Rate**, backed by **12 passing security invariant unit tests**. [PAUSE]*
  >
  > *By enforcing cryptographic capability boundaries before target APIs are invoked, ControlPlane enables enterprises to deploy autonomous AI agents with absolute confidence. Thank you."*

* **TECHNICAL RATIONALE & KEY TAKEAWAYS**:
  - Summarizes verified empirical metrics (80 benchmark cases, 100% L3 compliance, 97.5% accuracy, 12 passing unit tests).
  - Delivers a strong, professional executive conclusion.

---

## 3. Post-Recording Summary Table

| Scene # | Time | Target Component | Core Metric / Invariant Verified |
| :--- | :--- | :--- | :--- |
| **Scene 1** | 0:00 - 0:40 | Command Center | Pre-Execution Boundary: $\text{NO AUTHORIZATION} \implies \text{CALLS} = 0$ |
| **Scene 2** | 0:40 - 1:25 | Scenario A (Safe Query) | Sub-10ms L0 Routing & HMAC Token Execution (`CATALOG CALLS: 1`) |
| **Scene 3** | 1:25 - 2:10 | Scenario B (Flow A Response) | Flow A Grounding Inspection & Hallucination Interception (`CALLS: 0`) |
| **Scene 4** | 2:10 - 3:05 | Scenario C (Payment Rejected) | $BI \ge 75 \implies$ Mandatory L3 Floor & Human Rejection (`PAYMENT CALLS: 0`) |
| **Scene 5** | 3:05 - 3:50 | Scenario D (Payment Approved) | Human Approval HMAC Token & Single-Use Nonce Validation (`PAYMENT CALLS: 1`) |
| **Scene 6** | 3:50 - 4:25 | Scenario E (Prompt Injection) | Responsibility Engine $R_{resp} = 1.0 \implies$ Rule 1 Hard `BLOCK` (`CALLS: 0`) |
| **Scene 7** | 4:25 - 5:05 | Audit & Integrity | SHA-256 Hash Chain ($H_n = \text{SHA256}(P_n \parallel H_{n-1})$) & Tamper Reset |
| **Scene 8** | 5:05 - 5:35 | Executive Summary | 80-case Benchmark (100% L3, 97.5% Accuracy) & 12 Security Unit Tests |
