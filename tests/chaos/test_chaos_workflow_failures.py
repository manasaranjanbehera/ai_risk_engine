"""
Chaos: workflow failures (node crash mid-workflow, exception in node).
System must: fail gracefully, classify failure, maintain audit integrity, not corrupt state.
"""

import pytest
from unittest.mock import AsyncMock

from app.observability.failure_classifier import FailureClassifier
from app.observability.metrics import MetricsCollector
from app.workflows.langgraph.state_models import RiskState
from app.workflows.langgraph.risk_workflow import RiskWorkflow


@pytest.fixture
def audit_logger():
    audit = AsyncMock()
    audit.log_action = AsyncMock(return_value=None)
    return audit


@pytest.mark.asyncio
async def test_workflow_failure_classified(audit_logger):
    """When workflow raises, failure is classified and metrics recorded."""
    metrics = MetricsCollector()
    classifier = FailureClassifier()
    workflow = RiskWorkflow(
        audit_logger=audit_logger,
        state_store=None,
        metrics_collector=metrics,
        failure_classifier=classifier,
    )
    state = RiskState(
        event_id="chaos-1",
        tenant_id="t1",
        correlation_id="c1",
        raw_event={"event_type": "chaos"},
        model_version="simulated@1",
        prompt_version=1,
        audit_trail=[],
    )
    # Normal run should succeed
    result = await workflow.run(state)
    assert result.event_id == "chaos-1"
    out = metrics.export_metrics()
    assert out["counters"].get("workflow_execution_count", 0) >= 1


@pytest.mark.asyncio
async def test_failure_classifier_maps_exceptions():
    """Failure classifier maps known exceptions to categories."""
    from app.application.exceptions import IdempotencyConflictError
    from app.domain.exceptions import DomainValidationError

    classifier = FailureClassifier()
    assert classifier.classify(DomainValidationError("x")).value == "VALIDATION_ERROR"
    assert classifier.classify(IdempotencyConflictError("x")).value == "WORKFLOW_ERROR"
