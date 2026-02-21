# Phase 5 — Governance & Security: Development Summary

**Objective:** Make the AI Risk Engine bank-ready by adding governance and security modules. No FastAPI in these layers; all components dependency-injected; clean architecture boundaries preserved.

---

## 1. Architectural objectives

- **Traceability:** Every action is auditable (who, what, when UTC, why, correlation_id).
- **Controlled deployment:** Every model requires approval; unapproved models cannot be deployed.
- **Versioning:** Every prompt is versioned with immutable history and change reason/author.
- **Isolation:** Every tenant is strictly isolated; no cross-tenant access.
- **Least privilege:** Every permission is enforced via a defined RBAC matrix.
- **Confidentiality:** Sensitive values can be protected via AES encryption (key from environment).
- **Human-in-the-loop:** Approval workflows require explicit human approval; no auto-approve; RBAC enforced.

---

## 2. Modules implemented

### Governance (`app/governance/`)

| Module | Purpose |
|--------|--------|
| **audit_models.py** | Immutable `AuditRecord` (frozen dataclass): actor, tenant_id, action, resource_type, resource_id, reason, correlation_id, metadata, timestamp_utc. |
| **audit_repository.py** | `AuditRepository` protocol: `async def save(record: AuditRecord) -> None`. |
| **audit_logger.py** | `AuditLogger.log_action(...)` builds an immutable record and persists via repository; structured JSON at storage boundary. |
| **model_registry.py** | `ModelRegistry`: `register_model`, `approve_model`, `reject_model`, `get_model`, `get_approved_model`. `ModelRecord` with model_name, version, checksum, created_at, approved, approved_by, approved_at, status (PENDING/APPROVED/REJECTED). Approval and rejection emit audit log. |
| **prompt_registry.py** | `PromptRegistry`: `register_prompt`, `update_prompt`, `get_prompt`. Version increments; change_reason and author stored; previous versions immutable; every change audited. |
| **approval_workflow.py** | `ApprovalWorkflow`: `request_approval`, `approve`, `reject`. Status transitions (only PENDING → APPROVED or REJECTED); RBAC (only APPROVER or ADMIN may approve/reject); audit trail on every state change. |
| **exceptions.py** | `GovernanceError`, `ModelNotApprovedError`, `InvalidModelStateError`, `InvalidWorkflowStateError`. |

### Security (`app/security/`)

| Module | Purpose |
|--------|--------|
| **rbac.py** | `Role` enum: ADMIN, ANALYST, APPROVER, VIEWER. `RBACService.check_permission(role, action)`; raises `AuthorizationError` if denied. |
| **tenant_context.py** | `TenantContext.validate_access(resource_tenant, request_tenant)`; raises `TenantIsolationError` on mismatch or empty tenant. |
| **encryption.py** | `EncryptionService(key)` (key from constructor or `ENCRYPTION_KEY` env); AES via Fernet; `encrypt(data: str) -> str`, `decrypt(data: str) -> str`; fails if key missing; no global mutable state. |
| **exceptions.py** | `SecurityError`, `AuthorizationError`, `TenantIsolationError`, `EncryptionError`. |

---

## 3. Security guarantees added

- **RBAC:** All sensitive actions (create, approve, view, register_model) are gated by `RBACService.check_permission(role, action)`. Unknown or disallowed (role, action) pairs raise `AuthorizationError`.
- **Tenant isolation:** `TenantContext.validate_access(resource_tenant, request_tenant)` must be used before returning or mutating tenant-scoped resources; cross-tenant access raises `TenantIsolationError`.
- **Encryption:** Sensitive strings can be encrypted at rest using `EncryptionService`; key must be provided (env or constructor); wrong or missing key raises `EncryptionError` on decrypt or init.

---

## 4. Governance guarantees added

- **Audit enforcement:** All model approvals/rejections and prompt register/update, and approval workflow state changes, go through `AuditLogger.log_action` with actor, tenant_id, action, resource_type, resource_id, reason, correlation_id. Records are immutable (`AuditRecord` frozen).
- **Model approval gate:** `ModelRegistry.get_approved_model(name, version)` raises `ModelNotApprovedError` if the model is not in APPROVED status; deploy paths must use this (or equivalent) to block unapproved models.
- **No double approval:** `approve_model` raises `InvalidModelStateError` if the model is already APPROVED or REJECTED.
- **Approval workflow transitions:** Only PENDING requests can be approved or rejected; otherwise `InvalidWorkflowStateError` is raised.
- **Prompt versioning:** Each update creates a new version; previous versions remain immutable; every change is audited.

---

## 5. Audit enforcement description

- **What is logged:** Actor (who), action (what), timestamp_utc (when), reason (why), correlation_id, resource_type, resource_id, optional metadata.
- **Where:** Audit records are written via the `AuditRepository` protocol. Implementations (e.g. DB or log sink) persist structured JSON; the domain does not mutate records after creation.
- **When:** On model approve/reject, prompt register/update, and approval request/approve/reject. Application layer can also call `AuditLogger.log_action` for other critical operations.

---

## 6. RBAC matrix

| Role    | Create | Approve | View | Register Model |
|---------|--------|---------|------|-----------------|
| ADMIN   | ✓      | ✓       | ✓    | ✓               |
| ANALYST | ✓      | ✗       | ✓    | ✗               |
| APPROVER| ✗      | ✓       | ✓    | ✗               |
| VIEWER  | ✗      | ✗       | ✓    | ✗               |

Actions are checked via `RBACService.check_permission(role, action)` with action one of: `"create"`, `"approve"`, `"view"`, `"register_model"`. Any other action or denied combination raises `AuthorizationError`.

---

## 7. Tenant isolation strategy

- **Rule:** A request may only access resources whose `tenant_id` matches the request’s tenant (e.g. from context or header).
- **Enforcement:** Before returning or mutating a tenant-scoped resource, call `TenantContext.validate_access(resource_tenant, request_tenant)`. If they differ or either is empty, `TenantIsolationError` is raised.
- **Scope:** Applied consistently at API/application boundary when resolving resources by ID; no cross-tenant data leakage.

---

## 8. Encryption approach

- **Algorithm:** AES via Fernet (cryptography library); key derived from a secret using PBKDF2-HMAC-SHA256 (configurable salt and iterations).
- **Key source:** Passed into `EncryptionService(key=...)` or read from `ENCRYPTION_KEY` environment variable if key is not provided. Empty or missing key raises `EncryptionError` at construction.
- **No global state:** Each `EncryptionService` instance is configured with a key; no module-level singleton holding secrets.
- **Usage:** `encrypt(plaintext: str) -> str` (returns base64-encoded ciphertext); `decrypt(ciphertext: str) -> str`. Wrong key or tampered data raises `EncryptionError` on decrypt.

---

## 9. Risk mitigation improvements

- **Operational risk:** Audit trail supports post-incident analysis and regulatory examination.
- **Model risk:** Only approved models can be used for deployment (`get_approved_model`); approval/rejection are logged and non-repudiable.
- **Prompt risk:** Versioned prompts with immutable history and change reason/author reduce drift and support rollback and accountability.
- **Access risk:** RBAC and tenant isolation limit blast radius of compromised credentials or misconfiguration.
- **Data risk:** Encryption allows protection of sensitive configuration or PII at rest when required.

---

## 10. How this improves regulatory posture

- **Traceability:** Regulators can demand “who did what, when, and why.” Immutable audit records and correlation_id support that.
- **Model governance:** Explicit approval workflow and “no deploy unapproved” align with model risk management expectations.
- **Access control:** Documented RBAC matrix and tenant isolation support access control and segregation requirements.
- **Encryption:** Supports requirements for encryption of sensitive data at rest when policy mandates it.
- **Human oversight:** Human-in-the-loop approval (no auto-approve) supports governance expectations for high-impact decisions.

---

## 11. Remaining gaps for Phase 6

- **Persistence:** Concrete implementations of `AuditRepository`, `ModelRegistryRepository`, `PromptRegistryRepository`, and `ApprovalRepository` (e.g. PostgreSQL or append-only store) and wiring in dependency injection.
- **API integration:** HTTP endpoints and middleware that inject governance/security services, enforce tenant and correlation context, and call RBAC and tenant validation on each request where needed.
- **Key management:** Formal key lifecycle for `ENCRYPTION_KEY` (rotation, vault integration) and key derivation parameters (salt, iterations) as configuration.
- **Observability:** Metrics and tracing for audit volume, approval latency, and permission denials; integration with existing observability stack.
- **Testing:** Integration tests against real or test implementations of repositories and full approval/model/prompt flows; optional load tests for audit write path.

---

## 12. Running Phase 5 unit tests

From the project root, with dependencies installed (e.g. `pip install -r requirements.txt`):

```bash
pytest tests/unit/governance tests/unit/security -v
```

Ensure `ENCRYPTION_KEY` is not set to an empty value when running tests that rely on a missing key (or use the test that patches the environment). All other tests use explicit keys or mocks and do not require external services.

---

*Phase 5 transforms the system from a backend service into a regulated AI platform foundation: every action auditable, every model gated by approval, every prompt versioned, every tenant isolated, every permission enforced, and every sensitive value encryptable.*
