# CONTROLPLANE.AI — Real-Time AI Assurance & Intervention Layer

> **"ControlPlane does not merely observe AI risk. It dynamically determines the required level of assurance and can intervene before a risky AI action reaches the target system."**

---

## 1. Executive Product Vision & Core Invariant

ControlPlane.ai is a real-time inline AI governance proxy designed for enterprises deploying LLM agents, generative AI applications, and autonomous tool-using workflows.

### Primary Technical Invariant
$$\text{NO VALID CONTROLPLANE AUTHORIZATION} \implies \text{NO TARGET ACTION EXECUTION (\text{TARGET API CALLS} = 0)}$$

---

## 2. Core Capabilities & Hero Features

- **Action Interception Gateway**: Prevents AI agents from possessing direct credentials to downstream payment, database, or API systems.
- **Dynamic Assurance Routing (L0–L3)**: Escalates evaluation depth dynamically based on business impact, cost deviation, and uncertainty.
- **L3 Critical Action Assurance Floor**: Irreversible or high-impact actions ($BI \ge 75$) enforce an un-bypassable `HUMAN_REVIEW` requirement before cryptographic token issuance.
- **Base64url HMAC-SHA256 Approval Tokens**: Action-bound authorization capability tokens (`base64url(payload).base64url(signature)`) bound to single-use nonces, action parameters hash, and policy versions.
- **Strict Target Verification Gateway**: Target endpoints (`/mock/catalog`, `/mock/payment`) enforce a 10-step cryptographic verification protocol and track atomic `target_api_call_count`.
- **Tamper-Evident SHA-256 Audit Chain**: Event log linked via $H_n = \text{SHA256}(P_n \parallel H_{n-1})$ with real-time integrity verification (`AUDIT INTEGRITY: VALID` vs `AUDIT INTEGRITY: BROKEN`).

---

## 3. Three Hero Demo Scenarios

1. **SCENARIO A — SAFE (Informational Query)**:
   Customer FAQ Request $\rightarrow$ L0 Fast Assurance $\rightarrow$ `ALLOW` $\rightarrow$ HMAC Approval Token $\rightarrow$ Executed via `/mock/catalog` $\rightarrow$ **`TARGET API CALLS: 1`**.
2. **SCENARIO B — HIGH IMPACT (₹50,00,000 Payment)**:
   Payment Request $\rightarrow$ $BI = 87 \ge 75 \rightarrow$ L3 Critical Action Floor $\rightarrow$ `HUMAN_REVIEW` $\rightarrow$ Human REJECT $\rightarrow$ Direct target execution attempt $\rightarrow$ **`HTTP 403 Forbidden`**, **`TARGET API CALLS: 0`**.
3. **SCENARIO C — MALICIOUS (Prompt Injection / Secret Leak)**:
   Prompt Injection Payload $\rightarrow$ Responsibility Violation $\rightarrow$ `BLOCK` $\rightarrow$ No token issued $\rightarrow$ **`TARGET API CALLS: 0`**.
4. **APPROVED PAYMENT PATH**:
   ₹50L Payment Request $\rightarrow$ L3 Pending Review $\rightarrow$ Human APPROVE $\rightarrow$ HMAC Approval Token issued $\rightarrow$ Executed via `/mock/payment` $\rightarrow$ **`TARGET API CALLS: 1`**.

---

## 4. Quick Start & Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ / npm

### Step 1: Backend Setup & Policy Seeding
```bash
# Navigate to backend and install requirements
pip install -r backend/requirements.txt

# Seed governance policy fixtures
python scripts/seed_policies.py

# Start FastAPI backend server (Port 8000)
python backend/app/main.py
```

### Step 2: Frontend Enterprise Control Center
```bash
# Navigate to frontend and install dependencies
cd frontend
npm install

# Start Next.js development server (Port 3000)
npm run dev
```

Open `http://localhost:3000` in your browser to interact with the Enterprise Control Center.

---

## 5. Security Test Suite Execution

Run all 12 non-negotiable security invariant tests:
```bash
python -m pytest backend/tests/security/test_action_guard.py -v
```

Run synthetic evaluation benchmark:
```bash
python scripts/run_evaluation.py
```
