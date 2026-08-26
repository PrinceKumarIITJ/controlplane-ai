# ControlPlane.ai — Technical Architecture Documentation

---

## 1. System Topology & Dual Governance Flow Architecture

ControlPlane.ai acts as an inline assurance and governance control plane positioned between AI models/agents and external target enterprise APIs.

```mermaid
graph TD
    Client[AI Agent / LLM App] -->|Payload| Interceptor[Interceptor Service]
    
    subgraph Governance Pipeline
        Interceptor --> Router[Assurance Router L0-L3]
        Router --> Engines[Risk Engines Inspection]
        Engines --> PerfEngine[Performance Engine]
        Engines --> CostEngine[Cost Engine]
        Engines --> RespEngine[Responsibility Engine]
        Engines --> BIEngine[Business Impact Engine]
        
        PerfEngine --> DecisionEngine[Decision Engine]
        CostEngine --> DecisionEngine
        RespEngine --> DecisionEngine
        BIEngine --> DecisionEngine
        
        DecisionEngine --> PolicyEngine[Policy Engine Rules]
    end

    PolicyEngine -->|ALLOW| TokenSvc[HMAC Token Service]
    PolicyEngine -->|HUMAN_REVIEW| ReviewQueue[L3 Human Review Queue]
    PolicyEngine -->|BLOCK / RECHECK / REROUTE| Intervene[Intervention Service]

    ReviewQueue -->|Approve| TokenSvc
    ReviewQueue -->|Reject| Intervene

    TokenSvc -->|HMAC Approval Token| ActionGuard[Target Action Guard]
    ActionGuard -->|Valid Token| TargetSys[Target Enterprise API]
    ActionGuard -->|Invalid / Missing Token| BlockTarget[403 Forbidden - 0 Calls]

    Governance Pipeline -->|Audit Log Event| AuditChain[Tamper-Evident Hash Chain]
```

---

## 2. Dual Governance Flows

### Flow A — Response Governance (AI $\rightarrow$ ControlPlane $\rightarrow$ User)
* **Goal**: Validate AI text claims against verified internal policy knowledge chunks before output is delivered to the user.
* **Pipeline**:
  1. AI text response payload received at `POST /api/v1/govern/response`.
  2. Performance Engine computes grounding status (`SUPPORTED`, `UNVERIFIED`, `CONTRADICTED`) against knowledge base chunks.
  3. Decision Engine evaluates risk and issues `RECHECK` or intervention message if unverified claims exist.
  4. Returns `ResponseGovernanceResponse` to client with optional rewritten intervention text.

### Flow B — Action Governance (AI Agent $\rightarrow$ ControlPlane $\rightarrow$ Target System)
* **Goal**: Intercept structured tool calls and prevent unauthorized target execution.
* **Pipeline**:
  1. Agent action proposal received at `POST /api/v1/govern/action`.
  2. Assurance Router computes Business Impact ($BI$) and routes to assurance level (L0–L3).
  3. If $BI \ge 75$ or critical action type, routes to **L3 Floor** $\rightarrow$ `HUMAN_REVIEW`. Token is withheld (`null`).
  4. Upon human reviewer approval at `POST /api/v1/review/{action_id}`, an **HMAC-SHA256 Approval Token** is issued.
  5. Client sends token in header `X-ControlPlane-Approval-Token` to `POST /mock/payment`.
  6. Action Guard validates signature, TTL, parameter hash, policy version, and atomically consumes single-use nonce.

---

## 3. 4-Tier Assurance Routing Matrix

| Tier | Target Scope | Checks Executed | Latency Budget | Default Decision |
| :--- | :--- | :--- | :--- | :--- |
| **L0** | Safe Informational Queries | Regex PII/Secrets, static cost bounds | $<10\text{ ms}$ | `ALLOW` |
| **L1** | Standard Tool Calls | Grounding cosine similarity, token cost deviation | $<50\text{ ms}$ | `ALLOW` / `REROUTE` |
| **L2** | Deep Response Inspection | Knowledge base chunk verification, policy tracing | $<500\text{ ms}$ | `RECHECK` |
| **L3** | Critical Action Floor | $BI \ge 75 \lor \text{Irreversible Action}$ | $<100\text{ ms}$ | **Mandatory `HUMAN_REVIEW`** |

---

## 4. Multi-Dimensional Risk Engine Specifications

ControlPlane evaluates risk across 6 transparent technical dimensions:

### 1. Performance Risk ($R_{perf}$)
Calculates evidence grounding status against policy knowledge chunks:
$$R_{perf} = \begin{cases} 0.0 & \text{if SUPPORTED (similarity } \ge 0.85) \\ 0.65 & \text{if UNVERIFIED (similarity } < 0.60) \\ 1.0 & \text{if CONTRADICTED} \end{cases}$$

### 2. Cost Risk ($R_{cost}$)
Calculates token usage deviation factor ($D = \text{Estimated Tokens} / \text{Expected Baseline}$):
$$R_{cost} = \min\left(1.0, \frac{D}{5.0}\right)$$
*If $D \ge 3.5\times$, triggers automated `REROUTE` decision.*

### 3. Responsibility Risk ($R_{resp}$)
Scans input parameters and prompts for Tier 1 (PII, API Keys, AWS Secrets) and Tier 2 (Prompt Injection, SQL/Command Injection) violations:
$$R_{resp} = \max(R_{tier1}, R_{tier2})$$
*If $R_{resp} \ge 0.80$, triggers immediate hard `BLOCK` decision.*

### 4. Normalized Business Impact ($BI$)
$$BI = 0.40 \times \text{Financial Impact} + 0.25 \times \text{Reversibility} + 0.20 \times \text{Data Sensitivity} + 0.15 \times \text{External Impact}$$
* **Financial Impact**: $\min(100, \text{Amount} / 50000)$.
* **Reversibility**: `IRREVERSIBLE` = 100, `PARTIALLY_REVERSIBLE` = 50, `EASILY_REVERSIBLE` = 0.
* **Data Sensitivity**: `RESTRICTED_PII` = 100, `CONFIDENTIAL` = 60, `INTERNAL` = 30, `PUBLIC` = 0.
* **External Impact**: `EXTERNAL_FINANCIAL` = 100, `CUSTOMER_FACING` = 60, `INTERNAL_ONLY` = 10.
* **L3 Threshold**: $BI \ge 75 \implies \text{L3 Floor (Mandatory HUMAN\_REVIEW)}$.

### 5. Detection Confidence ($DC$)
Measures certainty of inspection engines ($0.0 - 1.0$). High $BI$ ($BI \ge 75$) combined with low confidence ($DC < 0.60$) triggers `HUMAN_REVIEW`.

### 6. Composite Risk ($CR$)
Policy-weighted aggregate score:
$$CR = 0.30 \times R_{perf} + 0.20 \times R_{cost} + 0.30 \times R_{resp} + 0.20 \times \left(\frac{BI}{100}\right)$$

---

## 5. Sequential Decision Precedence Rules

Decision Engine evaluates rules in strict order:

1. **Hard Security Violation**: $R_{resp} \ge 0.80 \implies$ **`BLOCK`**
2. **Assurance Level Floor**: Assurance == `L3` $\implies$ **`HUMAN_REVIEW`**
3. **High Impact + Low Confidence**: $BI \ge 75 \land DC < 0.60 \implies$ **`HUMAN_REVIEW`**
4. **Excessive Cost Anomaly**: $D \ge 3.5\times \implies$ **`REROUTE`**
5. **High Composite Risk**: $CR \ge 0.65 \implies$ **`BLOCK`**
6. **Moderate Risk / Grounding Issue**: $CR \ge 0.40 \lor \text{UNVERIFIED} \implies$ **`RECHECK`**
7. **Default**: **`ALLOW`**

---

## 6. Action Guard & HMAC-SHA256 Approval Token Design

$$\text{Token Signature} = \text{HMAC-SHA256}(\text{Secret}, \text{CanonicalPayload})$$

### Action-Bound Capability Token Payload
The Approval Token is an action-bound capability token (not a JWT user session token). It binds:
* `token_id`, `action_id`, `action_type`, `target`
* `parameters_hash`: $\text{SHA256}(\text{canonical\_json}(\text{parameters}))$
* `decision_id`, `application_id`, `policy_id`, `policy_version`
* `nonce`: Unique single-use cryptographic string
* `issued_at`, `expires_at` (Default TTL = 300 seconds)

### Target Action Guard Verification Checklist
Target endpoints (`POST /mock/payment`, `POST /mock/catalog`) verify:
1. Header `X-ControlPlane-Approval-Token` presence.
2. Constant-time HMAC-SHA256 signature verification using server secret `CONTROLPLANE_TOKEN_SECRET`.
3. Expiration check (`expires_at > current_timestamp`).
4. `action_id` & `target` string equality.
5. Parameter hash match ($	ext{SHA256}(	ext{parameters}) == 	ext{parameters\_hash}$).
6. Single-use `nonce` status check & atomic update from `ISSUED` to `CONSUMED` in SQLite. Replay attempts return `401 Unauthorized` and yield **0 target API calls**.

---

## 7. Tamper-Evident SHA-256 Audit Hash Chain

Audit events are appended to a cryptographically linked ledger:

$$H_n = \text{SHA256}(\text{Payload}_n \parallel H_{n-1})$$

* **Verification**: `POST /api/v1/audit/verify` recalculates $H_1 \dots H_n$ sequentially. If any payload or hash is mutated, verification fails with **`AUDIT INTEGRITY: BROKEN`**.
* **Reset**: `POST /api/v1/audit/reset` re-anchors event hashes and restores valid audit state after tamper simulation tests.
