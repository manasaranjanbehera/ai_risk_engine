🎯 Objective

Implement Phase 7 — Observability & Production Hardening for ai_risk_engine.

You must:

Implement all observability modules.

Integrate with existing workflows (Phase 6).

Add latency, cost, tenant usage, and failure tracking.

Write comprehensive unit tests.

Run all tests.

Fix failures.

Ensure 100% test pass.

Update documentation.

Create a development phase summary.

Maintain clean architecture boundaries.

Do NOT modify unrelated layers.

No real external SaaS calls — simulate exporters safely.

📂 DIRECTORY STRUCTURE

Create:

app/observability/

Structure:

observability/
├── metrics.py
├── tracing.py
├── langfuse_client.py
├── evaluation.py
├── cost_tracker.py
└── failure_classifier.py
🔭 OBSERVABILITY REQUIREMENTS
1️⃣ metrics.py — Prometheus-Style Metrics

Implement:

class MetricsCollector:

Must track:

request_count (by tenant)

workflow_execution_count

node_execution_latency (histogram style)

request_latency

failure_count (by category)

approval_required_count

model_usage_count

prompt_usage_count

Expose:

def increment(...)
def observe_latency(...)
def export_metrics() -> dict

No real Prometheus dependency required — simulate Prometheus-style registry.

Must be thread-safe.

2️⃣ tracing.py — OpenTelemetry-Style Tracing

Implement:

class TracingService:
    async def start_span(...)
    async def end_span(...)

Features:

Trace ID propagation

Span hierarchy (workflow → nodes)

Latency tracking

Attach:

tenant_id

correlation_id

model_version

prompt_version

Store traces in memory exporter

No real OTLP export required.

3️⃣ langfuse_client.py — LLM Trace Logging

Simulate Langfuse-style client:

class LangfuseClient:
    async def log_generation(...)

Track:

prompt_version

model_version

input_tokens

output_tokens

estimated_cost

latency

tenant_id

event_id

Must integrate with:

cost_tracker.py

metrics.py

No external calls.

4️⃣ evaluation.py — Quality Scoring

Implement:

class EvaluationService:
    async def evaluate_decision(...)

Must calculate:

confidence_score (deterministic)

policy_alignment_score

guardrail_score

overall_quality_score

Store evaluation result in workflow state.
Emit audit event.

5️⃣ cost_tracker.py

Track:

cost per request

cost per tenant

cost per model version

cumulative cost

Expose:

def add_cost(...)
def get_tenant_cost(...)

Use deterministic cost estimation (e.g., token_count × fixed rate).

6️⃣ failure_classifier.py

Categorize failures into:

VALIDATION_ERROR

POLICY_VIOLATION

HIGH_RISK

WORKFLOW_ERROR

INFRA_ERROR

UNEXPECTED_ERROR

Expose:

def classify(exception) -> FailureCategory

Must integrate with:

MetricsCollector

AuditLogger

🔗 WORKFLOW INTEGRATION

Update:

app/workflows/langgraph/

Integrate observability hooks:

Each node must:

Start span

Measure latency

Log metrics

Log cost (if LLM simulated)

Log prompt/model usage

Capture failures

End span

Workflow must:

Record total request latency

Record per-node latency

Track approval required metrics

Track tenant usage

Track cost

📊 REQUIRED METRICS

System must now support:

Latency per node

Total workflow latency

Cost per request

Cost per tenant

Model usage count

Prompt usage count

Failure categorization count

Tenant usage metrics

Approval escalation metrics

🧪 TESTING REQUIREMENTS

Create:

tests/unit/observability/
Metrics Tests

Counter increments correctly

Histogram tracks latency

Tenant metrics separated

Failure metrics increment correctly

Tracing Tests

Trace ID created

Span nesting correct

Latency recorded

Metadata attached

Langfuse Client Tests

Generation log recorded

Cost computed

Metrics updated

Evaluation Tests

Deterministic quality scoring

Scores within bounds

Audit emitted

Cost Tracker Tests

Cost accumulates per tenant

Cost per model tracked

Reset works

Failure Classifier Tests

Each exception maps correctly

Unknown exception → UNEXPECTED_ERROR

Workflow Integration Tests

Node latency recorded

Cost tracked

Model usage counted

Prompt usage counted

Failure classified properly

Metrics reflect execution

Approval-required increments counter

🧪 EXECUTION REQUIREMENT

After implementing:

Run:

pytest tests/unit/observability
pytest tests/unit/workflows

Fix any failures.
Re-run until all pass.
No skipped tests allowed.

📚 DOCUMENTATION UPDATE

Update:

docs/PROJECT_STRUCTURE.md
docs/FOLDER_AND_FILE_STRUCTURE.md

Add Observability layer description.

Explain:

Metrics strategy

Tracing strategy

Cost tracking approach

Failure categorization

Production hardening approach

📝 DEVELOPMENT SUMMARY

Create:

app/docs/development-phase/PHASE_7_OBSERVABILITY_AND_PRODUCTION_HARDENING.md

Readable format including:

Architectural objective

Observability architecture diagram explanation

Metrics catalog

Tracing hierarchy design

Cost governance model

Failure taxonomy

Tenant metering strategy

Latency instrumentation

Production readiness improvements

Scalability considerations

Future SaaS exporter integration plan

Professional enterprise engineering tone.

🔐 ARCHITECTURAL RULES

No FastAPI imports

No external SaaS calls

Deterministic cost estimation

Thread-safe metrics registry

Async compatible tracing

No global mutable state

Dependency injected services

All timestamps UTC

Structured logging only

🎯 POST-PHASE 7 SYSTEM CAPABILITIES

After this phase, your platform must support:

Full auditability

Deterministic AI workflows

Model & prompt version governance

Cost transparency

Latency visibility

Failure taxonomy

Tenant metering

Approval tracking

Observability-ready production core

This transitions your system from:

AI Risk Engine → Enterprise-Production AI Platform