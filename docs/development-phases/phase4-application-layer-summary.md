# Phase 4 — Application Layer Summary

Summary of what was implemented for **Phase 4 — Application Layer** (Transaction Boundary / Orchestration).

---

## 1. Domain

- **`app/domain/models/event.py`**  
  Added `EventStatus.RECEIVED` and transition `RECEIVED` → `VALIDATED` / `REJECTED`.

- **`app/domain/validators/event_validator.py`**  
  Included `RECEIVED` in allowed status transitions.

---

## 2. Application Exceptions

- **`app/application/exceptions.py`**  
  Defines (separate from domain exceptions):
  - `ApplicationError` (base)
  - `IdempotencyConflictError`
  - `MessagingFailureError`

---

## 3. Event Repository

- **`app/application/event_repository.py`**  
  - `EventRepository` protocol: `save(event, correlation_id) -> PersistedEvent`, `get(tenant_id, event_id) -> Optional[PersistedEvent]`
  - `PersistedEvent` dataclass (event_id, tenant_id, correlation_id, status, created_at, metadata, version)

- **`app/infrastructure/cache/event_repository_redis.py`**  
  `RedisEventRepository` implements the protocol (Redis as event store, 7-day TTL).

---

## 4. Workflow Trigger

- **`app/workflows/interface.py`**  
  `WorkflowTrigger` protocol: `async def start(event_id, tenant_id) -> None`.

- **`app/workflows/dummy_workflow.py`**  
  `DummyWorkflowTrigger` — logs only (placeholder).

---

## 5. EventService

**`app/application/event_service.py`** refactored to:

- **Constructor**  
  All dependencies injected: `repository`, `publisher`, `redis_client`, `workflow_trigger`, `logger`.

- **Single entry point**  
  `async def create_event(self, event, tenant_id, idempotency_key, correlation_id) -> EventResponse`.

- **Flow (strict order)**  
  1. **Idempotency** — Redis key `idempotency:{tenant_id}:{idempotency_key}`; if hit → return cached response, log `idempotent_replay`.
  2. **Persist** — `repository.save(event, correlation_id)` (status `RECEIVED`).
  3. **Publish** — RabbitMQ exchange `risk_events`, routing `risk.created` / `compliance.created`; on failure → raise `MessagingFailureError`, **do not** cache idempotency.
  4. **Workflow** — `workflow_trigger.start(...)`; on failure → log and continue (workflow does not fail the transaction).
  5. **Audit** — Structured log `event_created` (event_id, tenant_id, correlation_id, event_type, status `RECEIVED`).
  6. **Cache idempotency** — Store full `EventResponse` JSON in Redis, TTL 300s.
  7. **Return** — `EventResponse` (mapped from persisted model).

- **Read path**  
  `get_event(tenant_id, event_id)` — uses repository `get`, returns `EventResponse` or `None`.

- **Constraints**  
  No FastAPI/HTTP, no global infra; structured logging at each step.

---

## 6. API and DI

- **`app/api/dependencies.py`**  
  Builds `EventService` with `RedisEventRepository`, `RabbitMQPublisher`, `RedisClient`, `DummyWorkflowTrigger`, logger; adds `get_correlation_id(request)`.

- **`app/api/routers/events.py`**  
  Validates request, builds `RiskEvent` / `ComplianceEvent`, calls `create_event`; handles `ApplicationError` / `MessagingFailureError` (503 / 500).

- **`app/api/routers/risk.py`** and **`app/api/routers/compliance.py`**  
  Build domain events and call `create_event` with `correlation_id`.

---

## 7. Tests

- **`tests/unit/application/test_event_service.py`**  
  Covers: happy path, idempotent replay, messaging failure (no idempotency cache), repository failure (publisher/workflow not called), workflow failure (success still returned).

- **`tests/unit/api/conftest.py`**  
  Added `mock_publisher` and overrides for `get_redis_client` and `get_publisher`.

- **`tests/unit/api/test_risk.py`**, **test_events.py**, **test_compliance.py**  
  Expect `status == "received"`.

---

## 8. Transaction and Behavior

- **Source of truth** — DB (persistence) is primary; messaging is secondary.
- **Messaging failure** — Transaction fails, idempotency not cached, `MessagingFailureError` raised.
- **Workflow failure** — Logged only; response still returned and idempotency cached.

---

## Running Tests

```bash
# Application-layer unit tests
pytest tests/unit/application -v

# All unit tests
pytest tests/unit -v
```
