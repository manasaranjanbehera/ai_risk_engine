# Project Review (Post–Phase 4) & Next Phase: Governance & Security

This document reviews the **ai_risk_engine** project after Phase 4 (Application Layer), then outlines considerations for the **Governance & Security** phase. **No implementation is done here**—only feedback and planning.

---

## 1. What’s Working Well

### Architecture

- **Layered boundaries** — Domain has no infra; application has no HTTP/FastAPI; API builds domain events and calls `create_event`. Clear separation.
- **Single entry point** — `EventService.create_event` is the only creation path; idempotency, persist, publish, workflow, and audit are in one place.
- **Transaction strategy** — Documented and implemented: persistence is primary; messaging failure fails the transaction (no idempotency cache); workflow failure is best-effort (log only).
- **DI** — Repository, publisher, redis, workflow trigger, and logger are injected; no globals inside the service.
- **Structured logging** — Steps log with `tenant_id`, `correlation_id`, `event_id` where available; event names (`idempotency_check`, `event_persisted`, etc.) match the spec.

### Domain & Application

- **EventStatus.RECEIVED** — Clearly represents “persisted at application boundary”; transitions are consistent in models and validators.
- **Application exceptions** — Separate from domain; `MessagingFailureError` used correctly on publish failure.
- **EventRepository protocol** — Clean contract (`save`, `get`); `RedisEventRepository` is a plausible implementation for current needs.
- **WorkflowTrigger** — Protocol + dummy keeps the design open for real workflows later.

### API & Infra

- **Routers** — Events, risk, and compliance all validate, build domain events, and call `create_event` with `correlation_id`; consistent pattern.
- **Middleware** — Correlation ID, tenant context, and request audit are in place and used by dependencies.
- **Tests** — Unit tests cover happy path, idempotent replay, messaging failure (no cache), repository failure, and workflow failure (success still returned).

---

## 2. Gaps, Risks & Inconsistencies

### 2.1 Application layer depends on infrastructure types

- **Observation:** `event_service.py` imports `RedisClient` and `RabbitMQPublisher` from `app.infrastructure`.
- **Impact:** Application layer is tied to concrete infra types. For strict “clean architecture,” the application would depend only on abstractions (e.g. protocols) defined in the application or a “ports” package; infrastructure would implement those.
- **Recommendation:** Acceptable for now. If you later need to swap Redis or RabbitMQ, introduce protocols (e.g. `IdempotencyStore`, `EventPublisher`) in the application layer and implement them in infrastructure. Low priority unless you plan multiple backends.

### 2.2 Event persistence: Redis only, no DB

- **Observation:** Events are stored in Redis (`RedisEventRepository`), not in PostgreSQL. The spec mentioned “DB transaction” and “primary source of truth”; the existing schema has `jobs`, `audit_logs`, `job_events`, but no dedicated `events` table.
- **Impact:** Event history is volatile (TTL 7 days); no single source of truth in the DB for events; harder to join with `jobs` / `audit_logs` for reporting.
- **Recommendation:** For Governance & Security (audit, compliance), consider either:
  - Adding an `events` (or similar) table and a DB-backed `EventRepository` that writes there (and optionally still use Redis for cache/read path), or
  - Explicitly documenting “event store = Redis” and ensuring audit/governance flows consume from RabbitMQ or a separate store. Decide before heavy audit requirements.

### 2.3 Global singletons in dependencies

- **Observation:** `get_redis_client()` and `get_publisher()` use module-level singletons. Tests override them via `app.dependency_overrides`.
- **Impact:** Fine for a single process; can complicate testing if multiple app instances or more complex DI are needed later.
- **Recommendation:** Acceptable. If you introduce a proper DI container or factory later, you can replace these with scoped lifetimes.

### 2.4 Tenant ID and correlation ID trust

- **Observation:** `tenant_id` comes from `X-Tenant-ID`; `correlation_id` from header or generated. There is no authentication/authorization yet.
- **Impact:** Any client can send any tenant ID; no proof of identity or authorization. Fine for internal/dev; not for production without security.
- **Recommendation:** Governance & Security phase should introduce authentication (e.g. JWT, API keys) and enforce that the authenticated identity is allowed to act for the given `tenant_id` (tenant binding / RBAC).

### 2.5 Audit: logs only, no persistent audit store

- **Observation:** Audit is done via structured logs (`event_created`, `request_audit` in middleware). There is no write to `audit_logs` or another persistent audit store.
- **Impact:** Audit trail lives only in log aggregation; no queryable DB table for compliance reports or “who did what when.”
- **Recommendation:** Governance & Security phase should define an audit service that writes to `audit_logs` (or equivalent) with actor, action, previous/new state, and correlation/tenant, and call it from the application layer or middleware.

### 2.6 No global handler for ApplicationError

- **Observation:** Routers catch `ApplicationError` / `MessagingFailureError` and return 503/500. There is no `@app.exception_handler(ApplicationError)` in `main.py`.
- **Impact:** If a future code path raises `ApplicationError` and doesn’t catch it, the generic `Exception` handler will return 500 with a generic message.
- **Recommendation:** Optional: add a global handler for `ApplicationError` (and optionally `MessagingFailureError`) so all application-layer errors are mapped consistently (e.g. 503 for messaging, 500 for others).

### 2.7 RabbitMQPublisher: connection lifecycle

- **Observation:** Publisher connects on first `publish()`; there is no explicit disconnect or health check.
- **Impact:** Long-lived processes are fine; in serverless or short-lived workers you might want connect/disconnect or connection pooling. Not critical for current design.
- **Recommendation:** Document “lazy connect, long-lived” and revisit when you add health checks (e.g. `/health` probing RabbitMQ).

---

## 3. Recommendations Before Starting Governance & Security

1. **Run tests** — Ensure `pytest tests/unit/application` and `pytest tests/unit/api` pass in your environment (pytest was not installed in the earlier check).
2. **Optional: DB event store** — If you want events as first-class DB entities for audit/compliance, add an `events` table and a DB-backed `EventRepository` (or a second implementation) and wire it via config/DI; keep Redis for idempotency/cache if desired.
3. **Optional: ApplicationError handler** — Add `@app.exception_handler(ApplicationError)` in `main.py` for consistent error responses.
4. **Docs** — Keep FOLDER_AND_FILE_STRUCTURE and PROJECT_STRUCTURE in sync when you add governance/security modules.

---

## 4. Next Phase: Governance & Security — What to Consider (No Implementation)

Use this as a checklist when you **do** implement Governance & Security.

### 4.1 Security

- **Authentication** — Verify the caller (e.g. JWT, API key). You already have `JWT_SECRET`, `jwt_algorithm`, `jwt_expiration_minutes` in settings; use them for token validation.
- **Authorization / tenant binding** — Ensure the authenticated identity is allowed to act for the `tenant_id` in the request (e.g. tenant membership, RBAC). Reject with 403 if not.
- **API security** — HTTPS in production; rate limiting (Redis is already used elsewhere; could add rate_limit to critical routes); input validation (you already have Pydantic + domain validators).
- **Secrets** — No secrets in code; use env/settings and secret managers in production.
- **Security headers** — Consider middleware for CSP, HSTS, etc., if the API serves or redirects to UI.

### 4.2 Governance

- **Audit persistence** — Persist audit events to `audit_logs` (or equivalent): actor, action, resource, previous/new state, tenant_id, correlation_id, timestamp. Call from EventService (e.g. after “event_created”) and/or from middleware for HTTP access.
- **Prompt / model registry** — If the system will use LLM prompts or model configs, consider a registry (e.g. in DB or config) with versioning and change history for compliance.
- **Approval workflows** — Schema already has `escalations`; link events/jobs to approval flows and record decisions in audit.
- **Data retention and deletion** — Policy for how long events, jobs, and audit logs are kept; secure deletion when required by regulation.

### 4.3 Where it fits in the stack

- **Security** — Middleware (auth, tenant binding) and possibly a `app/security/` package (auth service, token validation, permissions). API layer enforces “only if authorized.”
- **Governance** — `app/governance/` for audit service, registry, approval policies. Application layer (e.g. EventService) or middleware calls the audit service; workflows can drive approvals and escalations.
- **Existing pieces** — `audit_logs`, `escalations`, `jobs` in the schema; middleware already logs request-level audit. Extend to persistent audit and tie to tenant/actor/action.

### 4.4 Non-goals for this note

- No code or schema changes are made in this document.
- No new packages or endpoints are added; this is planning only.

---

## 5. Summary

- **Phase 4** is in good shape: clear transaction boundary, idempotency, structured logging, and sensible failure handling. The main trade-offs are Redis-only event persistence and application-layer imports of infra types; both are acceptable for now.
- **Before Governance & Security:** Run tests; optionally add a DB event store and a global `ApplicationError` handler.
- **Governance & Security phase:** Plan for authentication, tenant-bound authorization, persistent audit (e.g. `audit_logs`), and governance features (registry, approvals, retention) using the existing schema and middleware as a base.
