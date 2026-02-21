# Phase 4 — Application Layer (Cursor prompt)

🎯 Objective

Implement Phase 4 — Application Layer (Transaction Boundary / Orchestration Brain) for ai_risk_engine.

File:

app/application/event_service.py

This layer is the transaction boundary of the system.

It must:

Receive validated domain event

Enforce idempotency

Persist event (Repository layer)

Publish to RabbitMQ

Trigger workflow (placeholder hook)

Emit audit log

Be fully async

Be testable

Contain NO HTTP logic

Contain NO FastAPI imports

Contain NO direct infrastructure wiring (use DI)

No LLM integration yet.

🏗 Architectural Rules

This is a regulated AI platform.

Therefore:

EventService = orchestration only

Domain validation already completed in API layer

All dependencies injected

All operations structured-logged

Idempotency must be deterministic

Failures must roll back safely

Messaging failure must not corrupt DB state

🧱 1️⃣ Refactor / Implement EventService

Expected constructor:

```python
class EventService:
    def __init__(
        self,
        repository: EventRepository,
        publisher: RabbitMQPublisher,
        redis_client: RedisClient,
        workflow_trigger: WorkflowTrigger,  # interface placeholder
        logger: Logger,
    ):
```

Dependencies must NOT be created internally.

🧱 2️⃣ Public API

Implement:

```python
async def create_event(
    self,
    event: BaseEvent,
    tenant_id: str,
    idempotency_key: str,
    correlation_id: str,
) -> EventResponse
```

This is the only entry point.

🧱 3️⃣ Required Flow (Strict Order)
Step 1 — Idempotency Enforcement

Redis key format:

`idempotency:{tenant_id}:{idempotency_key}`

If exists:

Return cached response

Log: "idempotent_replay"

If not:

Continue

TTL = 300 seconds

Step 2 — Persist Event

Call repository:

`await repository.save(event)`

Must:

Store status = RECEIVED

Store tenant_id

Store correlation_id

Return persisted model with ID

Wrap in DB transaction if session supports it.

Step 3 — Publish to RabbitMQ

Exchange: "risk_events"
Routing key: based on event type:

RiskEvent → "risk.created"

ComplianceEvent → "compliance.created"

Message payload must include:

event_id

tenant_id

correlation_id

event_type

status

If publish fails:

Log error

Raise ApplicationError

DO NOT cache idempotency key

Step 4 — Trigger Workflow (Placeholder)

Call:

`await workflow_trigger.start(event_id=..., tenant_id=...)`

This should be a placeholder interface in:

app/workflows/interface.py

Implementation may be a dummy class for now.

Step 5 — Emit Audit Log

Structured log:

```json
{
  "event": "event_created",
  "event_id": "...",
  "tenant_id": "...",
  "correlation_id": "...",
  "event_type": "...",
  "status": "RECEIVED"
}
```

Use JSON logger.

Step 6 — Cache Idempotency Result

Store full serialized EventResponse in Redis for 5 minutes.

Step 7 — Return EventResponse

Must map from domain → schema.

🧱 4️⃣ Add Application-Level Exceptions

Create:

app/application/exceptions.py

Add:

ApplicationError

IdempotencyConflictError

MessagingFailureError

Do NOT reuse domain exceptions.

🧱 5️⃣ Workflow Trigger Interface

Create:

app/workflows/interface.py

Define:

```python
class WorkflowTrigger(Protocol):
    async def start(self, event_id: str, tenant_id: str) -> None:
        ...
```

Also create dummy implementation:

app/workflows/dummy_workflow.py

That just logs.

🧪 6️⃣ Unit Tests (Mandatory)

Create:

tests/unit/application/test_event_service.py

Use pytest + pytest-asyncio.

Mock:

repository

publisher

redis_client

workflow_trigger

Test Cases Required
✅ 1. Happy Path

No idempotency key exists

Event persisted

Publisher called

Workflow triggered

Audit logged

Redis cache set

✅ 2. Idempotent Replay

Redis key exists

Repository NOT called

Publisher NOT called

Workflow NOT called

Returns cached response

✅ 3. Messaging Failure

Repository save succeeds

Publisher throws exception

Idempotency NOT cached

Exception raised

✅ 4. Repository Failure

Save throws exception

Publisher NOT called

Workflow NOT called

✅ 5. Workflow Failure

Decide strategy:

If workflow fails, should NOT fail entire transaction

Log error but return success

Test this behavior.

🧠 Transaction Strategy Decision

Implement:

DB persistence is primary source of truth

Messaging is secondary

Workflow failure does NOT break transaction

Messaging failure DOES break transaction

Log reasoning in code comments.

🧾 Logging Requirements

Every step must include structured logs:

idempotency_check

event_persisted

event_published

workflow_triggered

idempotency_cached

event_creation_failed

Must include:

tenant_id

correlation_id

event_id (when available)

🚫 Forbidden

No FastAPI imports

No request objects

No global redis instances

No global DB session

No try/except swallowing

No print statements

📦 Expected Deliverables

Cursor should:

Refactor event_service.py properly

Add application exceptions

Add workflow interface + dummy

Add comprehensive unit tests

Use async everywhere

Respect clean architecture boundaries

🧪 Validation

After generation:

pytest tests/unit/application

Must pass.

🔎 Architectural Reminder

Phase 3 = Surface exposure
Phase 4 = Brain wiring

This is where your system becomes:

Deterministic

Replay-safe

Audit-traceable

Messaging-aware

Workflow-enabled

You are now building real backend architecture — not just FastAPI endpoints.
