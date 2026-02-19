# AI Risk Engine — Folder and File Structure

This document describes the current folder and file layout of the **ai_risk_engine** project (excluding `.git` and `__pycache__`). Use it as a quick reference for where code and assets live.

**Last generated:** February 18, 2025

---

## Complete directory tree

```
ai_risk_engine/
├── .gitignore
├── README.md
├── pyproject.toml
├── docker-compose.yml
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   └── event_service.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   ├── middleware.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── compliance.py
│   │       ├── events.py
│   │       ├── health.py
│   │       ├── risk.py
│   │       └── tenant.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── model_routing.py
│   │   ├── security.py
│   │   └── settings.py
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── event.py
│   │   ├── policies/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── event.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   └── validators/
│   │       ├── __init__.py
│   │       └── event_validator.py
│   │
│   ├── governance/
│   │   ├── __init__.py
│   │   ├── approval_workflow.py
│   │   ├── audit_logger.py
│   │   ├── model_registry.py
│   │   └── prompt_registry.py
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── cache/
│   │   │   └── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   └── session.py
│   │   ├── llm/
│   │   │   └── __init__.py
│   │   ├── messaging/
│   │   │   ├── __init__.py
│   │   │   └── rabbitmq_publisher.py
│   │   ├── tools/
│   │   │   └── __init__.py
│   │   └── vectorstore/
│   │       └── __init__.py
│   │
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── evaluation.py
│   │   ├── langfuse_client.py
│   │   ├── metrics.py
│   │   └── tracing.py
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   ├── encryption.py
│   │   ├── rbac.py
│   │   └── tenant_context.py
│   │
│   └── workflows/
│       ├── __init__.py
│       └── langgraph/
│           ├── __init__.py
│           ├── compliance_workflow.py
│           ├── risk_workflow.py
│           ├── state_models.py
│           └── nodes/
│               ├── __init__.py
│               ├── decision.py
│               ├── guardrails.py
│               ├── policy_validation.py
│               ├── retrieval.py
│               └── risk_scoring.py
│
├── docker/                    # (empty — Dockerfiles/scripts go here)
├── migrations/                 # (empty — DB migrations go here)
├── scripts/                   # (empty — utility/seed scripts go here)
│
├── tests/
│   ├── unit/                  # (empty)
│   ├── integration/           # (empty)
│   ├── load/                  # (empty)
│   └── workflow/              # (empty)
│
└── docs/
    ├── PROJECT_STRUCTURE.md           # Guide to project layout and conventions
    ├── FOLDER_AND_FILE_STRUCTURE.md   # This file — full tree reference
    └── llm_context/
        └── master_architecture_prompt.md
```

---

## File inventory by area

### Root

| File | Description |
|------|-------------|
| `.gitignore` | Git ignore rules |
| `README.md` | Project overview and run instructions |
| `pyproject.toml` | Python project config and dependencies |
| `docker-compose.yml` | Local services (app, DB, etc.) |

### Application (`app/`)

| Path | Description |
|------|-------------|
| `app/main.py` | Application entrypoint (FastAPI app) |
| `app/application/event_service.py` | Event application service (orchestrates domain + infrastructure) |
| `app/api/dependencies.py` | Shared API dependencies (e.g. auth, DB session) |
| `app/api/middleware.py` | HTTP middleware |
| `app/api/routers/compliance.py` | Compliance API routes |
| `app/api/routers/events.py` | Events API routes |
| `app/api/routers/health.py` | Health check routes |
| `app/api/routers/risk.py` | Risk API routes |
| `app/api/routers/tenant.py` | Tenant API routes |
| `app/domain/models/event.py` | Event domain model |
| `app/domain/schemas/event.py` | Event request/response schemas |
| `app/domain/validators/event_validator.py` | Event validation logic |
| `app/infrastructure/database/models.py` | Database ORM models |
| `app/infrastructure/database/repository.py` | Database repository (CRUD, queries) |
| `app/infrastructure/database/session.py` | Database session factory and dependency |
| `app/infrastructure/messaging/rabbitmq_publisher.py` | RabbitMQ message publisher |
| `app/config/settings.py` | Main settings / env config |
| `app/config/logging.py` | Logging configuration |
| `app/config/model_routing.py` | Model routing configuration |
| `app/config/security.py` | Security-related config |
| `app/governance/approval_workflow.py` | Approval workflow logic |
| `app/governance/audit_logger.py` | Audit logging |
| `app/governance/model_registry.py` | Model registry |
| `app/governance/prompt_registry.py` | Prompt registry |
| `app/observability/evaluation.py` | Evaluation logic |
| `app/observability/langfuse_client.py` | Langfuse integration |
| `app/observability/metrics.py` | Metrics collection |
| `app/observability/tracing.py` | Tracing setup |
| `app/security/encryption.py` | Encryption utilities |
| `app/security/rbac.py` | Role-based access control |
| `app/security/tenant_context.py` | Tenant context handling |
| `app/workflows/langgraph/compliance_workflow.py` | LangGraph compliance workflow |
| `app/workflows/langgraph/risk_workflow.py` | LangGraph risk workflow |
| `app/workflows/langgraph/state_models.py` | Workflow state models |
| `app/workflows/langgraph/nodes/decision.py` | Decision node |
| `app/workflows/langgraph/nodes/guardrails.py` | Guardrails node |
| `app/workflows/langgraph/nodes/policy_validation.py` | Policy validation node |
| `app/workflows/langgraph/nodes/retrieval.py` | Retrieval node |
| `app/workflows/langgraph/nodes/risk_scoring.py` | Risk scoring node |

### Documentation (`docs/`)

| Path | Description |
|------|-------------|
| `docs/PROJECT_STRUCTURE.md` | Project structure guide and conventions |
| `docs/FOLDER_AND_FILE_STRUCTURE.md` | This file — full folder and file structure |
| `docs/llm_context/master_architecture_prompt.md` | LLM context / architecture prompt |

---

## Related docs

- **Project layout and conventions:** [docs/PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
- **Architecture / LLM context:** [docs/llm_context/master_architecture_prompt.md](./llm_context/master_architecture_prompt.md)
