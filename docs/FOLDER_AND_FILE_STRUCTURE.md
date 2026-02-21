# AI Risk Engine — Folder and File Structure

This document describes the current folder and file layout of the **ai_risk_engine** project (excluding `.git`, `__pycache__`, and `venv/`). Use it as a quick reference for where code and assets live.

**Last updated:** February 21, 2025 (Phase 4 — application layer: event service, repository protocol, workflows)

---

## Phase 4 application layer (summary)

The application layer is the **transaction boundary**: orchestration only, no HTTP/FastAPI, all dependencies injected.

- **`app/application/event_service.py`** — Single entry point `create_event(event, tenant_id, idempotency_key, correlation_id)`; flow: idempotency → persist → publish (RabbitMQ) → workflow trigger → audit log → cache idempotency → return `EventResponse`. Also `get_event(tenant_id, event_id)`.
- **`app/application/event_repository.py`** — `EventRepository` protocol (`save`, `get`) and `PersistedEvent` dataclass.
- **`app/application/exceptions.py`** — `ApplicationError`, `IdempotencyConflictError`, `MessagingFailureError` (do not reuse domain exceptions).
- **`app/workflows/interface.py`** — `WorkflowTrigger` protocol (`async def start(event_id, tenant_id)`).
- **`app/workflows/dummy_workflow.py`** — `DummyWorkflowTrigger` placeholder (logs only).
- **`app/infrastructure/cache/event_repository_redis.py`** — `RedisEventRepository` implements event persistence (Redis, 7-day TTL).

Domain: `EventStatus.RECEIVED` added; validators include RECEIVED in transitions.

---

## Phase 2 domain layer (summary)

The domain package (`app/domain/`) is self-contained and free of infrastructure:

- **`exceptions.py`** — Base `DomainError` and specific errors for validation, status transitions, tenant, risk threshold, and metadata.
- **`models/event.py`** — `EventStatus` enum (received → created → validated → processing → approved/rejected/failed), allowed transitions, `BaseEvent` with `transition_to()`, and entity types `RiskEvent`, `ComplianceEvent`.
- **`schemas/event.py`** — Pydantic request schemas (`RiskEventCreateRequest`, `ComplianceEventCreateRequest`) and `EventResponse`; validators for tenant_id, risk_score 0–100, JSON-serializable metadata, version.
- **`validators/event_validator.py`** — Pure functions that enforce domain rules and raise domain exceptions; used for both API request validation and entity validation.

Import the public API from `app.domain` (see `app/domain/__init__.py` for `__all__`).

---

## Complete directory tree

```
ai_risk_engine/
├── .env                    # Local env vars (not committed)
├── .env.example            # Template for .env; copy to .env and fill in
├── .gitignore
├── README.md
├── requirements.txt        # Python dependencies
├── schema.sql              # PostgreSQL schema dump (reference)
├── docker-compose.yml      # Local services (Postgres, RabbitMQ, Redis)
│
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app entrypoint, middleware, router registration
│   │
│   ├── core/               # Request-scoped context (e.g. correlation_id, tenant_id)
│   │   ├── __init__.py
│   │   └── context.py
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   ├── event_repository.py   # EventRepository protocol, PersistedEvent
│   │   ├── event_service.py      # create_event, get_event (transaction boundary)
│   │   └── exceptions.py         # ApplicationError, IdempotencyConflictError, MessagingFailureError
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py       # get_event_service, get_redis_client, get_publisher, get_correlation_id
│   │   ├── middleware.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py         # Health check (mounted in main)
│   │       ├── events.py        # POST/GET events (idempotent create_event)
│   │       ├── risk.py          # POST /risk (uses create_event)
│   │       ├── compliance.py    # POST /compliance (uses create_event)
│   │       └── tenant.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── logging.py      # JSON logging, log level from settings
│   │   └── settings.py     # Pydantic settings (env, .env)
│   │
│   ├── domain/
│   │   ├── __init__.py     # Re-exports models, schemas, validators, exceptions
│   │   ├── exceptions.py   # Domain errors (DomainError, DomainValidationError, etc.)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── event.py    # EventStatus, BaseEvent, RiskEvent, ComplianceEvent; status transitions
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── event.py    # RiskEventCreateRequest, ComplianceEventCreateRequest, EventResponse
│   │   ├── validators/
│   │   │   ├── __init__.py
│   │   │   └── event_validator.py  # Tenant, risk score, metadata, status transition validators
│   │   ├── policies/       # (placeholder)
│   │   └── services/       # (placeholder)
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   └── session.py
│   │   ├── messaging/
│   │   │   ├── __init__.py
│   │   │   └── rabbitmq_publisher.py
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py           # Redis client (idempotency, cache)
│   │   │   └── event_repository_redis.py  # RedisEventRepository (event store)
│   │   ├── llm/            # (placeholder)
│   │   ├── tools/          # (placeholder)
│   │   └── vectorstore/    # (placeholder)
│   │
│   ├── governance/         # (placeholder — approval, audit, registries)
│   ├── observability/      # (placeholder — metrics, tracing)
│   ├── security/           # (placeholder — encryption, RBAC, tenant)
│   └── workflows/
│       ├── __init__.py
│       ├── interface.py    # WorkflowTrigger protocol
│       └── dummy_workflow.py  # DummyWorkflowTrigger (placeholder)
│
├── docker/                 # (empty — Dockerfiles/scripts go here)
├── migrations/             # (empty — DB migrations go here)
├── scripts/                # Utility and connectivity test scripts
│   ├── test_db.py          # Test Postgres connectivity
│   ├── test_redis.py       # Test Redis connectivity
│   ├── test_rabbit.py      # Test RabbitMQ connectivity
│   └── test_repository.py  # Test repository CRUD (test_events)
│
├── tests/
│   ├── unit/
│   │   ├── application/    # EventService unit tests (Phase 4)
│   │   │   └── test_event_service.py
│   │   └── api/
│   ├── integration/
│   ├── load/
│   └── workflow/
│
└── docs/
    ├── PROJECT_STRUCTURE.md           # Guide to project layout and conventions
    ├── FOLDER_AND_FILE_STRUCTURE.md   # This file — full tree reference
    ├── TESTING_AND_LOCAL_SETUP.md     # How to run and test locally (venv → health)
    └── llm_context/
        └── master_architecture_prompt.md
```

---

## File inventory by area

### Root

| File | Description |
|------|-------------|
| `.env.example` | Template for required/optional env vars; copy to `.env` (includes JWT_SECRET, DATABASE_URL, REDIS_URL, RABBITMQ_URL) |
| `.gitignore` | Git ignore rules (venv, .env, IDE, etc.) |
| `README.md` | Project overview and quick start |
| `requirements.txt` | Python dependencies (FastAPI, uvicorn, pydantic-settings, asyncpg, aio_pika, SQLAlchemy, etc.) |
| `schema.sql` | PostgreSQL schema dump (reference); generate with `docker exec -t compliance_postgres pg_dump ...` |
| `docker-compose.yml` | Local services: Postgres, RabbitMQ, Redis |

### Application (`app/`)

| Path | Description |
|------|-------------|
| `app/main.py` | FastAPI app, context middleware (correlation/tenant headers), router includes |
| `app/core/context.py` | Context vars: `correlation_id_ctx`, `tenant_id_ctx` |
| `app/application/event_service.py` | Event application service: `create_event` (idempotency → persist → publish → workflow → audit → cache), `get_event`; transaction boundary, no HTTP |
| `app/application/event_repository.py` | `EventRepository` protocol (save, get), `PersistedEvent` dataclass |
| `app/application/exceptions.py` | Application errors: `ApplicationError`, `IdempotencyConflictError`, `MessagingFailureError` |
| `app/api/dependencies.py` | DI: `get_event_service`, `get_redis_client`, `get_publisher`, `get_tenant_id`, `get_correlation_id` |
| `app/api/routers/health.py` | Health check: `GET /health` (status, environment, version) — mounted in main |
| `app/api/routers/events.py` | Events API: POST/GET events; builds domain events, calls `create_event` |
| `app/api/routers/risk.py` | POST /risk — builds RiskEvent, calls `create_event` |
| `app/api/routers/compliance.py` | POST /compliance — builds ComplianceEvent, calls `create_event` |
| `app/infrastructure/cache/redis_client.py` | Redis async client (idempotency keys, cache) |
| `app/infrastructure/cache/event_repository_redis.py` | `RedisEventRepository`: persist events to Redis (status RECEIVED), 7-day TTL |
| `app/config/settings.py` | Main settings (Pydantic BaseSettings, `.env`) |
| `app/config/logging.py` | Logging config (JSON formatter, correlation/tenant in logs) |
| `app/domain/exceptions.py` | Domain errors: `DomainError`, `DomainValidationError`, `InvalidStatusTransitionError`, `InvalidTenantError`, `RiskThresholdViolationError`, `InvalidMetadataError` |
| `app/domain/models/event.py` | Event domain model: `EventStatus` (incl. RECEIVED), `BaseEvent` (with `transition_to()`), `RiskEvent`, `ComplianceEvent` |
| `app/domain/schemas/event.py` | Event request/response schemas: `RiskEventCreateRequest`, `ComplianceEventCreateRequest`, `EventResponse` (Pydantic; metadata JSON-serializable, risk 0–100) |
| `app/domain/validators/event_validator.py` | Pure validators: tenant_id, risk_score, metadata, status transition; request and entity validation |
| `app/infrastructure/database/models.py` | Database ORM models |
| `app/infrastructure/database/repository.py` | Database repository (CRUD, queries; e.g. AsyncRepository) |
| `app/infrastructure/database/session.py` | Database session factory and dependency |
| `app/infrastructure/messaging/rabbitmq_publisher.py` | RabbitMQ message publisher |
| `app/workflows/interface.py` | `WorkflowTrigger` protocol: `async def start(event_id, tenant_id)` |
| `app/workflows/dummy_workflow.py` | `DummyWorkflowTrigger` — placeholder implementation (logs only) |

### Scripts (`scripts/`)

| Script | Description |
|--------|-------------|
| `test_db.py` | Test Postgres connectivity |
| `test_redis.py` | Test Redis connectivity |
| `test_rabbit.py` | Test RabbitMQ connectivity |
| `test_repository.py` | Test repository CRUD (test_events table) |

### Tests (`tests/`)

| Path | Description |
|------|-------------|
| `tests/unit/application/test_event_service.py` | EventService unit tests: happy path, idempotent replay, messaging/repository/workflow failure (Phase 4) |
| `tests/unit/api/conftest.py` | API test fixtures: FakeRedis, mock_publisher, app_with_overrides |
| `tests/unit/api/test_events.py` | Events API: idempotency, validation, GET by id |
| `tests/unit/api/test_risk.py` | POST /risk: valid payload, validation failure, idempotency |
| `tests/unit/api/test_compliance.py` | POST /compliance: valid payload, validation, idempotency |

### Documentation (`docs/`)

| Path | Description |
|------|-------------|
| `docs/PROJECT_STRUCTURE.md` | Project structure guide and conventions |
| `docs/FOLDER_AND_FILE_STRUCTURE.md` | This file — full folder and file structure |
| `docs/TESTING_AND_LOCAL_SETUP.md` | Local setup and testing (venv, run app, health check) |
| `docs/llm_context/master_architecture_prompt.md` | LLM context / architecture prompt |

---

## Related docs

- **Project layout and conventions:** [docs/PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
- **Local setup and testing:** [docs/TESTING_AND_LOCAL_SETUP.md](./TESTING_AND_LOCAL_SETUP.md)
- **Architecture / LLM context:** [docs/llm_context/master_architecture_prompt.md](./llm_context/master_architecture_prompt.md)

Schema dump:
docker exec -t compliance_postgres pg_dump -U compliance_user -d compliance_db --schema-only > schema.sql
