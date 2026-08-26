# CONTROLPLANE.AI — PROTOTYPE BOUNDARIES & LIMITATIONS

---

## 1. Prototype Scope Statement

ControlPlane.ai is a working, verifiable prototype demonstrating a dynamic AI assurance and intervention layer. It is built to prove real-time interception, dynamic risk evaluation, cryptographic token authorization, and target enforcement boundaries.

---

## 2. Technical Limitations & Out-of-Scope Items

1. **Target Systems Integration**:
   - *Current*: Enforces authorization via mock endpoints `/mock/catalog` and `/mock/payment`.
   - *Production Requirement*: Downstream production APIs (Stripe, Plaid, SAP, AWS) must deploy an SDK or API gateway plugin enforcing token verification.
2. **AI Provider Abstraction**:
   - *Current*: Demo Mode runs offline with zero API cost using deterministic `MockAIProvider` fixtures.
   - *Production Requirement*: Enable real-time vector database retrieval (Pinecone/Weaviate) and OpenAI/Anthropic embeddings via `providers/base.py`.
3. **Database & Infrastructure**:
   - *Current*: SQLite database with SQLAlchemy ORM.
   - *Production Requirement*: Migrate to PostgreSQL with distributed Redis nonce caching for ultra-low latency single-use token invalidation.
4. **Authentication & Multi-Tenancy**:
   - *Current*: Basic role strings (`usr_compliance_lead`, `usr_emp_4412`).
   - *Production Requirement*: Enterprise OAuth2 / OIDC / SAML SSO integration with fine-grained RBAC.
