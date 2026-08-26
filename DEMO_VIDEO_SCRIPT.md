# ControlPlane.ai — Complete Demo Video Recording Script & Visual Storyboard

Target Video Duration: **3 minutes 30 seconds to 4 minutes**

---

## 1. Pre-Recording Technical Checklist

Before pressing record:
1. **Ensure Backend is Running**: `python backend/app/main.py` (Port 8000).
2. **Ensure Frontend is Running**: `cd frontend && npm run dev` (Port 3000).
3. **Open Browser Window**: Navigate to `http://localhost:3000` (Recommend 1920x1080 resolution, 100% zoom).
4. **Reset Execution Counters**: Click **"Reset Counters"** on the Command Center tab so `PAYMENT TARGET API CALLS: 0` and `CATALOG TARGET API CALLS: 0`.
5. **Verify Audit Chain**: Ensure bottom-left badge displays `AUDIT INTEGRITY: VALID`.

---

## 2. Minute-by-Minute Scene & Voiceover Script

| Timestamp | Visual Action (WHAT TO SHOW / CLICK) | Voiceover Script (EXACT SPOKEN WORDS) | Technical Concept Proved |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:30** | **Command Center Dashboard**<br>- Show `http://localhost:3000`<br>- Hover cursor over KPI cards.<br>- Highlight `PAYMENT TARGET API CALLS: 0`. | *"Welcome to ControlPlane.ai — a real-time AI assurance and intervention layer. As enterprise AI agents gain direct operational capabilities like transferring funds or modifying databases, traditional post-facto logging is no longer enough. ControlPlane sits inline between AI agents and enterprise APIs, enforcing a strict invariant: **No valid ControlPlane authorization means zero target action execution**."* | Pre-execution inline intervention vs post-hoc monitoring. |
| **0:30 - 1:00** | **Scenario A: Safe FAQ Query**<br>- Click **Live Hero Interceptor** tab.<br>- Click **"SCENARIO A — SAFE RESPONSE / QUERY"**.<br>- Highlight L0 Fast Assurance, `ALLOW`, HMAC Token issued, and target call `HTTP 200 OK`. | *"Let's test Scenario A — a safe, grounded FAQ request. ControlPlane evaluates the request in sub-10 milliseconds, assigns **L0 Fast Pass Assurance**, and approves the action. An action-bound **HMAC-SHA256 Approval Token** is issued to the target service. The mock catalog API validates the token and succeeds, incrementing target calls to 1."* | Sub-millisecond L0 routing & valid HMAC token capability execution (`CATALOG CALLS: 1`). |
| **1:00 - 1:30** | **Scenario B: Flow A Response Governance**<br>- Click **"SCENARIO B — UNSUPPORTED AI RESPONSE (FLOW A)"**.<br>- Highlight `UNVERIFIED` status, `RECHECK` decision, rewritten intervention message, and `TARGET API CALLS: 0`. | *"Next, Scenario B demonstrates Flow A Response Governance. Here, an AI model generates an ungrounded claim promising an unapproved ₹50 Lakh payment limit. ControlPlane's Performance Engine compares the claim against verified policy chunks, detects an **UNVERIFIED** grounding status, and triggers a **RECHECK** intervention. The ungrounded response is intercepted before reaching the user, with **zero target API calls**."* | Flow A response grounding verification & ungrounded claim interception (`TARGET CALLS: 0`). |
| **1:30 - 2:15** | **Scenario C: Flow B Action Governance (Payment Rejected)**<br>- Click **"SCENARIO C — HIGH IMPACT PAYMENT REJECTED"**.<br>- Show $BI = 87 \ge 75$, `L3 CRITICAL FLOOR`, `HUMAN_REVIEW` decision, Token = `null`.<br>- Show target call returned `HTTP 403 Forbidden`.<br>- Click **Human Review Queue** tab.<br>- Click **"REJECT ACTION"**. | *"In Scenario C, an AI agent attempts a high-impact ₹50 Lakh vendor payment. Because the Business Impact score is 87, exceeding our threshold of 75, ControlPlane enforces a mandatory **L3 Critical Action Floor**. The decision is set to **HUMAN_REVIEW** and the approval token is withheld. A direct attempt to call the payment target without a token returns **403 Forbidden**. Switching to the Human Review Queue, the compliance officer rejects the request, ensuring payment calls remain strictly **0**."* | Business Impact $BI \ge 75 \implies$ L3 Floor, mandatory human review, token withholding, and target rejection (`PAYMENT CALLS: 0`). |
| **2:15 - 2:45** | **Scenario D: Flow B Action Governance (Payment Approved)**<br>- Switch to **Live Hero Interceptor** tab.<br>- Click **"SCENARIO D — HIGH IMPACT PAYMENT APPROVED"**.<br>- Show human reviewer approves invoice INV-2026-99.<br>- Show HMAC Token generated.<br>- Show target output `HTTP 200 OK` (`PAYMENT TARGET API CALLS: 1`). | *"Now in Scenario D, we demonstrate valid human authorization for the same payment. After invoice verification, the human reviewer clicks Approve. ControlPlane generates a short-lived, action-bound HMAC-SHA256 Approval Token binding the action ID, target, and parameter digest. The Action Guard verifies the token signature and single-use nonce, allowing the payment target to execute successfully with **1 target call**."* | Human approval token generation, parameter hash binding, single-use nonce invalidation, & target execution (`PAYMENT CALLS: 1`). |
| **2:45 - 3:15** | **Scenario E: Malicious Prompt Injection**<br>- Click **"SCENARIO E — MALICIOUS RESPONSIBILITY VIOLATION"**.<br>- Show Responsibility Risk $R_{resp} = 1.0$, Decision = `BLOCK`, Token = `null`, `TARGET API CALLS: 0`. | *"In Scenario E, an attacker attempts a prompt injection to exfiltrate AWS API keys. ControlPlane's Responsibility Engine detects both secret leakage and injection patterns, assigning a Responsibility Risk of 1.0. Rule 1 triggers an immediate **BLOCK**, withholding tokens and preventing execution."* | Responsibility Engine scanning (Tier 1 Secrets & Tier 2 Prompt Injection) & immediate hard `BLOCK`. |
| **3:15 - 3:45** | **Tamper-Evident SHA-256 Audit Chain**<br>- Switch to **Audit & Integrity** tab.<br>- Show green `AUDIT INTEGRITY: VALID` badge.<br>- Click **"Simulate Tampering"** $ightarrow$ Show red `AUDIT INTEGRITY: BROKEN` badge.<br>- Click **"Reset Audit Integrity"** $ightarrow$ Show green `AUDIT INTEGRITY: VALID`. | *"To guarantee compliance immutability, all decisions are logged to a SHA-256 hash chain where each event hash incorporates the previous event's hash. If an attacker tampers with a database event record, our verification algorithm instantly flags **AUDIT INTEGRITY: BROKEN**. Resetting restores full cryptographic validity."* | Cryptographic SHA-256 audit hash chain ($H_n = 	ext{SHA256}(P_n \parallel H_{n-1})$) & tamper detection. |
| **3:45 - 4:00** | **Conclusion & Verification Metrics**<br>- Switch to **Command Center** tab.<br>- Summarize 80 benchmark cases, 100% L3 compliance, 97.5% decision accuracy, 12 passing security tests. | *"ControlPlane.ai delivers zero-trust pre-execution assurance for autonomous AI agents. With 100% L3 compliance, 97.5% decision accuracy across our 80-case benchmark, and 12 passing security invariant unit tests, ControlPlane proves that AI action safety can be mathematically enforced. Thank you."* | Executive wrap-up & empirical test suite verification. |

---

## 3. Post-Recording Verification Checklist

After recording your screen and audio:
- [ ] Verify video resolution is crisp (1080p recommended).
- [ ] Confirm voiceover audio is clear with no background noise.
- [ ] Confirm all 5 hero scenarios (Scenarios A through E) are clearly visible.
- [ ] Verify the target execution counter `PAYMENT TARGET API CALLS` is explicitly shown as `0` on rejection and `1` on approval.
- [ ] Confirm the red `AUDIT INTEGRITY: BROKEN` badge is shown during tamper simulation.
