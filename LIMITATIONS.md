# ControlPlane.ai — Prototype Boundaries & Production Roadmap

---

## 1. Prototype Scope Statement

ControlPlane.ai is a working, fully verifiable proof-of-concept prototype built to demonstrate real-time AI assurance, dynamic multi-dimensional risk evaluation, 4-tier assurance routing (L0–L3), cryptographic HMAC capability token authorization, and target system boundary enforcement.

---

## 2. Current Prototype Boundaries vs Production Requirements

### 1. Target Systems Integration
* **Current Prototype**: Implements illustrative mock target endpoints (`POST /mock/catalog` and `POST /mock/payment`) that enforce header `X-ControlPlane-Approval-Token`.
* **Production Requirement**: Production enterprise APIs (Stripe, Plaid, SAP, AWS, Salesforce) will deploy lightweight sidecar proxies or API Gateway middleware (Kong, Envoy) to inspect ControlPlane Approval Tokens.

### 2. Evidence Retrieval & Grounding Context
* **Current Prototype**: Operates in self-contained Demo Mode using deterministic policy knowledge chunks and in-memory similarity metrics.
* **Production Requirement**: Integration with production vector databases (Pinecone, Qdrant, Weaviate) and real-time LLM embedding providers (OpenAI, Anthropic, Cohere).

### 3. Storage & Distributed Nonce Tracking
* **Current Prototype**: Uses local SQLite storage (`controlplane.db`) with SQLAlchemy ORM.
* **Production Requirement**: Migration to managed PostgreSQL for structured audit persistence and Redis clusters for distributed sub-millisecond single-use nonce invalidation.

### 4. Enterprise Identity & Role Management
* **Current Prototype**: Simple identifier strings (`usr_compliance_lead`, `finance_agent_v2`).
* **Production Requirement**: Enterprise OAuth2 / OIDC / SAML 2.0 Single Sign-On (Okta, Azure AD) with fine-grained Attribute-Based Access Control (ABAC).

### 5. Benchmark & Dataset Scope
* **Current Prototype**: Synthetic 80-case regression evaluation dataset (`data/evaluation/dataset.json`).
* **Production Requirement**: Continuous real-time evaluation across live agent telemetry streams and adaptive shadow evaluation pipelines.

---

## 3. Production Evolution Roadmap

```
[Phase 1: Proof-of-Concept Prototype] (Current)
   ├── FastAPI Assurance Engine
   ├── Next.js Single-Page Control Center UI
   ├── Local SQLite & HMAC-SHA256 Token Service
   └── 80-Case Evaluation & 12 Security Unit Tests

[Phase 2: Enterprise Integration] (Next Step)
   ├── PostgreSQL & Redis Cluster Integration
   ├── API Gateway Sidecar (Kong / Envoy Plugin)
   ├── OIDC / SAML Enterprise Identity
   └── LangChain & LlamaIndex SDK Connectors

[Phase 3: Scale & Governance Platform]
   ├── Hardware Security Module (HSM) Secret Key Rotation
   ├── Dynamic Visual Policy Builder
   └── Automated Compliance Reporting (SOC2 / ISO 42001)
```
