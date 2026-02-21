🎯 Objective

Implement Phase 5 — Governance & Security for ai_risk_engine.

This phase makes the system bank-ready.

You must:

Implement all required modules.

Write comprehensive unit tests.

Run all new tests.

Fix any failures.

Ensure full test pass.

Update documentation.

Create development phase summary.

Respect clean architecture boundaries.

Do not modify unrelated layers.

🏛 PHASE 5 SCOPE
🔷 GOVERNANCE MODULES

Create under:

app/governance/
1️⃣ audit_logger.py
Purpose

Immutable audit logging for regulated traceability.

Requirements

Implement:

class AuditLogger:
    async def log_action(
        self,
        *,
        actor: str,
        tenant_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        reason: str | None,
        correlation_id: str,
        metadata: dict | None,
    ) -> None:
Behavior

Writes immutable audit record.

Must include:

who

what

when (UTC timestamp)

why

correlation_id

Must NOT allow mutation.

Must log structured JSON.

Store via repository (create simple AuditRepository interface).

No FastAPI imports.

Add domain-level immutability enforcement.

2️⃣ model_registry.py
Purpose

Track model versions + approval status.

Implement:

class ModelRegistry:
    async def register_model(...)
    async def approve_model(...)
    async def reject_model(...)
    async def get_model(...)
Required fields

model_name

version

checksum

created_at

approved (bool)

approved_by

approved_at

status (PENDING, APPROVED, REJECTED)

Enforce:

Cannot deploy unapproved model.

Approval must emit audit log.

3️⃣ prompt_registry.py
Purpose

Versioned prompt tracking.

Implement:

class PromptRegistry:
    async def register_prompt(...)
    async def update_prompt(...)
    async def get_prompt(...)

Must:

Track version

Store change_reason

Store author

Immutable previous versions

Audit every change

4️⃣ approval_workflow.py
Purpose

Human-in-the-loop gating.

Implement:

class ApprovalWorkflow:
    async def request_approval(...)
    async def approve(...)
    async def reject(...)

Rules:

Cannot auto-approve

Must enforce RBAC (only APPROVER role)

Must log audit trail

Status transitions enforced

🔐 SECURITY MODULES

Create under:

app/security/
5️⃣ rbac.py

Define:

class Role(Enum):
    ADMIN
    ANALYST
    APPROVER
    VIEWER

Implement:

class RBACService:
    def check_permission(role: Role, action: str) -> None:

Raise AuthorizationError if invalid.

Permission matrix:

Role	Create	Approve	View	Register Model
ADMIN	✓	✓	✓	✓
ANALYST	✓	✗	✓	✗
APPROVER	✗	✓	✓	✗
VIEWER	✗	✗	✓	✗

Must be unit tested thoroughly.

6️⃣ tenant_context.py

Implement strict tenant isolation:

class TenantContext:
    def validate_access(resource_tenant: str, request_tenant: str) -> None:

If mismatch → raise TenantIsolationError.

No cross-tenant access allowed.

7️⃣ encryption.py

Implement:

AES-based encryption wrapper (use cryptography library)

Methods:

encrypt(data: str) -> str

decrypt(data: str) -> str

Must:

Use environment key

Fail if key missing

Be unit tested

Avoid global state

🧪 TESTING REQUIREMENTS

Create under:

tests/unit/governance/
tests/unit/security/
Governance Tests

audit immutability

audit fields completeness

model cannot be approved twice

cannot deploy unapproved model

prompt version increments correctly

approval workflow enforces RBAC

status transitions enforced

Security Tests

RBAC permission matrix fully tested

tenant isolation enforced

encryption round-trip works

encryption fails with wrong key

cross-tenant access raises error

🧪 EXECUTION REQUIREMENT

After implementing:

Run:

pytest tests/unit/governance
pytest tests/unit/security

Fix any failures.

Ensure 100% pass rate.

Do not suppress failing tests.

📚 DOCUMENTATION UPDATE

Update:

docs/PROJECT_STRUCTURE.md
docs/FOLDER_AND_FILE_STRUCTURE.md

Add new governance and security sections.

📝 DEVELOPMENT SUMMARY

Create folder:

app/docs/development-phase/

Create file:

PHASE_5_GOVERNANCE_AND_SECURITY.md

Must include:

Architectural objectives

Modules implemented

Security guarantees added

Governance guarantees added

Audit enforcement description

RBAC matrix

Tenant isolation strategy

Encryption approach

Risk mitigation improvements

How this improves regulatory posture

Remaining gaps for Phase 6

Write as enterprise engineering documentation.

🔐 ARCHITECTURAL RULES

No FastAPI imports in governance/security layer.

No HTTP logic.

No global mutable state.

All components dependency-injected.

All exceptions typed.

All logs structured.

All timestamps UTC.

Immutability enforced where required.

📦 EXPECTED OUTPUT

Cursor must:

Implement 7 new modules

Add exceptions where needed

Add repositories/interfaces where required

Write comprehensive tests

Run and fix

Update docs

Create development summary file

Ensure full unit test pass

🧠 ARCHITECTURAL TARGET

After Phase 5:

Every action is auditable

Every model requires approval

Every prompt is versioned

Every tenant is isolated

Every permission is enforced

Every sensitive value is encrypted

Every change is traceable

This transforms the system from:

Backend Service → Regulated AI Platform