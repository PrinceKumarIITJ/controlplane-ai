# CONTROLPLANE.AI — HERO DEMO EXECUTION GUIDE

---

## Step 1: Start Backend & Frontend

1. Terminal 1: `python backend/app/main.py`
2. Terminal 2: `cd frontend && npm run dev`
3. Open `http://localhost:3000`

---

## Step 2: Present the Three Hero Scenarios

### Scenario 1 — Safe FAQ Query
- Click **"SCENARIO A — SAFE QUERY"** in the Hero tab.
- Observe: Classified as **L0 Fast Assurance**, Decision = **ALLOW**.
- An HMAC Approval Token is issued and sent to `/mock/catalog`.
- Target Response: `HTTP 200 OK`, **`CATALOG TARGET API CALLS: 1`**.

### Scenario 2 — High-Impact Vendor Payment (Human Rejection)
- Click **"SCENARIO B — HIGH IMPACT PAYMENT (REJECT)"** in the Hero tab.
- Observe: Business Impact $BI = 87 \ge 75$, assigned to **L3 Critical Action Assurance**.
- Precedence hits L3 Floor $\rightarrow$ Decision = **HUMAN_REVIEW**. Token = `null`.
- Direct agent attempt to invoke target without token yields **`HTTP 403 Forbidden`**, **`PAYMENT TARGET API CALLS: 0`**.
- Switch to **Human Review Queue** tab and click **REJECT**.
- Confirm status is updated to `REJECTED` and zero tokens were generated.

### Scenario 3 — Malicious Prompt Injection Attack
- Click **"SCENARIO C — MALICIOUS INJECTION"** in the Hero tab.
- Observe: Responsibility Engine flags secret leak & injection ($R_{resp} = 1.0$).
- Rule 1 triggers $\rightarrow$ Decision = **BLOCK**. Token = `null`.
- Target system execution denied $\rightarrow$ **`PAYMENT TARGET API CALLS: 0`**.

### Scenario 4 — Approved Payment Path
- Click **"APPROVED PAYMENT PATH"** button.
- Observe: Payment proposal hits L3 pending review $\rightarrow$ Human reviewer clicks **APPROVE** $\rightarrow$ HMAC Approval Token issued $\rightarrow$ Target execution succeeds $\rightarrow$ **`PAYMENT TARGET API CALLS: 1`**.

---

## Step 3: Present Tamper-Evident Audit Chain

- Switch to **Audit & Integrity** tab.
- Observe status badge: `AUDIT INTEGRITY: VALID`.
- Click **"Simulate Unauthorized DB Tampering"**.
- Observe status immediately flips to: **`AUDIT INTEGRITY: BROKEN (TAMPER DETECTED)`** highlighting the exact event ID altered.
