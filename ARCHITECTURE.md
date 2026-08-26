# CONTROLPLANE.AI — TECHNICAL ARCHITECTURE DOCUMENTATION

---

## 1. System Topology

ControlPlane.ai acts as an inline intervention proxy between AI agents and downstream target systems.

```
AI Agent / App ──> ControlPlane Interceptor ──> Assurance Router (L0-L3)
                                                        │
                                                        ▼
Target System <── Action Guard <── Token Svc <── Decision Engine <── Risk Engines
```

---

## 2. Assurance Routing Matrix

| Tier | Target Scope | Checks Executed | Latency Budget |
| :--- | :--- | :--- | :--- |
| **L0** | Safe Queries | Regex PII/Secrets, static cost bounds | $<10\text{ ms}$ |
| **L1** | Standard Actions | Grounding vector cosine check, token cost deviation | $<50\text{ ms}$ |
| **L2** | Deep Checks | Retrieval claim verification, deep policy tracing | $<500\text{ ms}$ |
| **L3** | Critical Floor | $BI \ge 75 \lor \text{Irreversible} \implies$ **Mandatory `HUMAN_REVIEW`** | $<100\text{ ms}$ (Automated) |

---

## 3. Normalized Business Impact Formula

$$BI = 0.40 \times \text{Financial Impact} + 0.25 \times \text{Reversibility} + 0.20 \times \text{Data Sensitivity} + 0.15 \times \text{External Impact}$$

- Financial Impact: $\min(100, \text{Amount} / 50000)$.
- Reversibility: `IRREVERSIBLE` = 100, `PARTIALLY_REVERSIBLE` = 50, `EASILY_REVERSIBLE` = 0.
- Data Sensitivity: `RESTRICTED_PII` = 100, `CONFIDENTIAL` = 60, `INTERNAL` = 30, `PUBLIC` = 0.
- External Impact: `EXTERNAL_FINANCIAL` = 100, `CUSTOMER_FACING` = 60, `INTERNAL_ONLY` = 10.

---

## 4. Sequential Decision Precedence

1. Hard Security Violation ($R_{resp} \ge 0.80$) $\rightarrow$ **`BLOCK`**
2. Assurance Level == L3 $\rightarrow$ **`HUMAN_REVIEW`**
3. High Impact ($BI \ge 75$) AND Low Confidence ($DC < 0.60$) $\rightarrow$ **`HUMAN_REVIEW`**
4. Excessive Cost Deviation ($D \ge 3.5\times$) $\rightarrow$ **`REROUTE`**
5. High Composite Risk ($CR \ge 0.65$) $\rightarrow$ **`BLOCK`**
6. Moderate Risk ($CR \ge 0.40$) OR Contradicted Grounding $\rightarrow$ **`RECHECK`** / **`EDIT`**
7. Default $\rightarrow$ **`ALLOW`**

---

## 5. Cryptographic Action Guard & Approval Token

$$\text{Token} = \text{base64url(payload\_json)} \,.\, \text{base64url(HMAC-SHA256(Secret, payload\_json))}$$

Target endpoints verify:
1. HMAC signature equality via constant-time comparison.
2. TTL expiration (`expires_at > now`).
3. Single-use `nonce` status in DB (Atomic update from `ISSUED` to `CONSUMED`).
4. Action parameters SHA-256 digest match (`parameters_hash`).
5. Policy version binding match.
