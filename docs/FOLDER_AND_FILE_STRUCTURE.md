# AI Risk Engine — Folder and File Structure

This document describes the current folder and file layout of the **ai_risk_engine** project (excluding `.git`, `__pycache__`, and `venv/`). Use it as a quick reference for where code and assets live.

**Last updated:** February 19, 2025

---

## Complete directory tree

```
ai_risk_engine/
├── .env                    # Local env vars (not committed)
├── .env.example            # Template for .env; copy to .env and fill in
├── .gitignore
├── README.md
├── requirements.txt        # Python dependencies
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
│   │   └── event_service.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── middleware.py   # (placeholder / minimal)
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py   # Health check endpoint
│   │       └── events.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── logging.py      # JSON logging, log level from settings
│   │   └── settings.py     # Pydantic settings (env, .env)
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── event.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── event.py
│   │   ├── validators/
│   │   │   ├── __init__.py
│   │   │   └── event_validator.py
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
│   │   ├── cache/          # (placeholder)
│   │   ├── llm/            # (placeholder)
│   │   ├── tools/          # (placeholder)
│   │   └── vectorstore/    # (placeholder)
│   │
│   ├── governance/         # (placeholder — approval, audit, registries)
│   ├── observability/      # (placeholder — metrics, tracing)
│   ├── security/           # (placeholder — encryption, RBAC, tenant)
│   └── workflows/          # (placeholder — LangGraph workflows)
│
├── docker/                 # (empty — Dockerfiles/scripts go here)
├── migrations/             # (empty — DB migrations go here)
├── scripts/                # (empty — utility/seed scripts go here)
│
├── tests/
│   ├── unit/
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
| `.env.example` | Template for required/optional env vars; copy to `.env` |
| `.gitignore` | Git ignore rules (venv, .env, IDE, etc.) |
| `README.md` | Project overview and quick start |
| `requirements.txt` | Python dependencies (FastAPI, uvicorn, pydantic-settings, etc.) |
| `docker-compose.yml` | Local services: Postgres, RabbitMQ, Redis |

### Application (`app/`)

| Path | Description |
|------|-------------|
| `app/main.py` | FastAPI app, context middleware, router includes |
| `app/core/context.py` | Context vars: `correlation_id_ctx`, `tenant_id_ctx` |
| `app/application/event_service.py` | Event application service (orchestrates domain + infrastructure) |
| `app/api/middleware.py` | HTTP middleware (minimal/placeholder) |
| `app/api/routers/health.py` | Health check: `GET /health` (status, environment, version) |
| `app/api/routers/events.py` | Events API routes |
| `app/config/settings.py` | Main settings (Pydantic BaseSettings, `.env`) |
| `app/config/logging.py` | Logging config (JSON formatter, correlation/tenant in logs) |
| `app/domain/models/event.py` | Event domain model |
| `app/domain/schemas/event.py` | Event request/response schemas |
| `app/domain/validators/event_validator.py` | Event validation logic |
| `app/infrastructure/database/models.py` | Database ORM models |
| `app/infrastructure/database/repository.py` | Database repository (CRUD, queries) |
| `app/infrastructure/database/session.py` | Database session factory and dependency |
| `app/infrastructure/messaging/rabbitmq_publisher.py` | RabbitMQ message publisher |

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
