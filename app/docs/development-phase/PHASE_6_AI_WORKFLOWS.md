# Phase 6 — AI Workflows (LangGraph Layer): Development Summary

**Objective:** Implement deterministic AI pipelines (LangGraph-style orchestration) for the AI Risk Engine with full auditability, version tracking, and idempotency. No real LLM integration in this phase; all model calls are simulated deterministically.

---

## 1. Architectural objectives

- **Deterministic AI pipelines:** Risk and compliance workflows execute a fixed sequence of nodes (retrieval → policy validation → risk scoring → guardrails → decision) with no randomness. Outcomes are reproducible for the same input state.
- **Auditable reasoning:** Every node emits an immutable audit record via `AuditLogger`, including action, correlation_id, tenant_id, and metadata (model version, prompt version, execution time). The state object carries an `audit_trail` of node executions for replay and debugging.
- **Version tracking:** Model version (from `ModelRegistry`) and prompt version (from `PromptRegistry`) are resolved at workflow start and logged at each stage, supporting regulated deployment and traceability.
- **Approval checkpoints:** Workflows set `final_decision` to `APPROVED` or `REQUIRE_APPROVAL` based on policy result, risk score, and guardrails. Compliance workflow adds regulatory-flag gating and `approval_required`. Integration with RBAC and human-in-the-loop approval (Phase 5) is respected at the boundary.
- **Tenant isolation:** State carries `tenant_id`; all audit records and workflow execution are tenant-scoped. Callers must ensure `TenantContext` validation when loading or persisting tenant-scoped resources.
- **Replay-safe and idempotent:** Workflow state can be cached by `event_id` (e.g. Redis key `workflow:{event_id}`). If a cached state exists, the workflow returns it without re-running nodes. Within a run, nodes already present in `audit_trail` are skipped, enabling safe replay and partial completion.

---

## 2. State machine design

- **RiskState** (Pydantic): `event_id`, `tenant_id`, `correlation_id`, `raw_event`, `retrieved_context`, `policy_result` (PASS/FAIL), `risk_score`, `guardrail_result`, `final_decision`, `model_version`, `prompt_version`, `audit_trail`, `idempotency_key`. All transitions are immutable: `state.transition(**updates)` returns a new instance; the original is never mutated.
- **ComplianceState:** Extends the same idea with `regulatory_flags` (list) and `approval_required` (bool). Used by the compliance workflow for regulatory gating.
- States are fully serializable (e.g. `model_dump_json` / `model_validate_json`) for storage in Redis and audit compatibility.

---

## 3. Node responsibilities

| Node | Responsibility | Deterministic behavior | Audit action |
|------|----------------|------------------------|--------------|
| **retrieval** | Simulate vector retrieval; set `retrieved_context` from `raw_event` (e.g. tenant + event_type). | Context string derived only from state. | `context_retrieved` |
| **policy_validation** | Rule-based validation: FAIL if `metadata.category == "sensitive"` or `policy_override`; else PASS. | No randomness. | `policy_validated` |
| **risk_scoring** | Score from event type and metadata: e.g. high_risk → 85, sensitive → 70, low_risk → 15, standard → 30. | Fixed mapping. | `risk_scored` |
| **guardrails** | Threshold (e.g. risk ≥ 75) and blocked patterns in metadata; set guardrail_result OK/VIOLATION. | Deterministic. | `guardrails_applied` |
| **decision** | If policy FAIL or high risk or guardrail VIOLATION → `REQUIRE_APPROVAL`; else `APPROVED`. | Deterministic. | `decision_made` |
| **compliance_decision** | Same as above plus: any `regulatory_flags` or approval conditions set `REQUIRE_APPROVAL` and `approval_required=True`; otherwise auto-approve. | Deterministic. | `decision_made` |

Each node is async, accepts state, returns a new state (no in-place mutation), and logs model_version, prompt_version, and execution time in audit metadata.

---

## 4. Deterministic reasoning explanation

- No random number generation or non-deterministic APIs in nodes. Outputs depend only on inputs (state fields and `raw_event`).
- Risk score, policy result, guardrail result, and final decision are computed via explicit rules (thresholds, categories, flags). Same input state always yields the same output state.
- This supports regulatory audit and replay: given the same event and versions, the system can reproduce the same decision and audit trail.

---

## 5. Governance hooks

- **AuditLogger:** Every node calls `audit_logger.log_action(...)` with actor `"workflow"`, resource_type `"workflow"`, resource_id `event_id`, and metadata containing `model_version`, `prompt_version`, and `execution_ms`.
- **ModelRegistry / PromptRegistry:** Optional constructor dependencies of `RiskWorkflow` and `ComplianceWorkflow`. If provided, the workflow resolves the current model version (e.g. for `"risk-model"`) and prompt version (e.g. for `"risk-prompt"`) at run start and sets them on state; nodes then include these in audit metadata. If not provided, default `simulated@1` and version `1` are used.
- **Approval integration:** Workflows set `final_decision` and (for compliance) `approval_required`. Downstream application or API layers can use `ApprovalWorkflow` and RBAC to gate actions when `REQUIRE_APPROVAL` is set.

---

## 6. Idempotency strategy

- **WorkflowStateStore** protocol: `get_risk_state(event_id)`, `set_risk_state(event_id, state, ttl_seconds)`.
- **RedisWorkflowStateStore:** Key `workflow:{event_id}` (and `workflow:compliance:{event_id}` for compliance). Serializes state to JSON; TTL configurable (default 3600s).
- **Run semantics:** On `run(state)`, if a store is configured and `get_*_state(state.event_id)` returns a cached state, that state is returned immediately and no nodes are executed. Otherwise, the pipeline runs; at the end, the final state is written to the store. This prevents double execution for the same event_id.
- **Replay within a run:** Before each node, the workflow checks whether that node’s name already appears in `state.audit_trail`. If so, the node is skipped. This allows resumable or replay-safe execution without re-running completed steps.

---

## 7. Audit guarantees

- Every node execution produces exactly one audit record via `AuditLogger`, with who (workflow), what (action), when (UTC), correlation_id, tenant_id, and metadata (model_version, prompt_version, execution_ms, and any result fields such as policy_result, risk_score, final_decision).
- The state’s `audit_trail` is appended to at each node with a structured entry (node name, action, timestamp, versions, execution_ms). This provides an in-state trace of the run for debugging and compliance.

---

## 8. Model and prompt version tracking

- Model version is read from `ModelRegistry.get_model(...)` (or default) at workflow start and stored on state; every node logs it in audit metadata.
- Prompt version is read from `PromptRegistry.get_prompt(...)` (or default) and similarly stored and logged.
- This satisfies requirements for tracking which model and prompt versions were used for each decision, without integrating a real LLM in this phase.

---

## 9. Approval integration

- Workflows emit decisions (`APPROVED` / `REQUIRE_APPROVAL`) and, for compliance, `approval_required`. They do not call `ApprovalWorkflow` directly; the application or API layer is responsible for creating approval requests and enforcing RBAC when `REQUIRE_APPROVAL` is set. This keeps the workflow layer free of HTTP and approval repository concerns while preserving the checkpoint semantics required for regulated AI.

---

## 10. Risk mitigation improvements

- **Determinism:** Reproducible behavior for the same inputs reduces “unknown” failure modes and supports incident replay.
- **Full audit trail:** Every step is logged with versions and timing, supporting root-cause analysis and regulatory review.
- **Idempotency:** Prevents duplicate workflow runs for the same event, reducing risk of inconsistent or double decisions.
- **Tenant isolation:** State and audit are tenant-scoped; workflow logic does not cross tenants.

---

## 11. Remaining gaps (LLM integration — Phase 7)

- **Real LLM calls:** Retrieval, scoring, and decision nodes currently use deterministic simulations. Phase 7 can replace these with actual model invocations (e.g. embedding + vector search for retrieval, LLM for scoring or decision) while preserving the same state shape, audit metadata, and version tracking.
- **Vector store:** Real retrieval will require a vector store integration; the current node only simulates context from `raw_event`.
- **Prompt templates:** When integrating an LLM, prompts can be loaded from `PromptRegistry` by version and injected into the nodes; model selection can use `ModelRegistry.get_approved_model(...)` to enforce approval before use.

---

## 12. Summary

Phase 6 transitions the system from a regulated backend with governance and security to an **AI Risk Engine** with deterministic, auditable AI pipelines. It introduces LangGraph-style workflow orchestration, immutable state transitions, model and prompt version tracking, idempotency, and clear approval checkpoints, without introducing real LLM or vector-store dependencies. All behavior is testable and replay-safe, and the design is ready for Phase 7 LLM integration.
