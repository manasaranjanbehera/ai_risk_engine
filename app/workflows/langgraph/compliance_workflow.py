"""Compliance workflow: retrieval → policy → scoring → guardrails → compliance decision."""

import logging
from typing import Optional

from app.governance.audit_logger import AuditLogger
from app.governance.model_registry import ModelRegistry
from app.governance.prompt_registry import PromptRegistry
from app.workflows.langgraph.nodes.compliance_nodes import (
    apply_guardrails_compliance,
    make_compliance_decision,
    retrieve_context_compliance,
    score_risk_compliance,
    validate_policy_compliance,
)
from app.workflows.langgraph.state_models import ComplianceState
from app.workflows.langgraph.workflow_state_store import ComplianceStateStore

logger = logging.getLogger(__name__)

DEFAULT_MODEL_VERSION = "simulated@1"
DEFAULT_PROMPT_VERSION = 1


def _node_done_compliance(state: ComplianceState, node: str) -> bool:
    return any((e.get("node") == node for e in state.audit_trail))


class ComplianceWorkflow:
    """
    Compliance workflow with additional compliance gating.
    Automatic approval if low regulatory flags; escalate otherwise.
    Idempotent when state_store is provided.
    """

    def __init__(
        self,
        audit_logger: AuditLogger,
        state_store: Optional[ComplianceStateStore] = None,
        model_registry: Optional[ModelRegistry] = None,
        prompt_registry: Optional[PromptRegistry] = None,
    ) -> None:
        self._audit = audit_logger
        self._store = state_store
        self._model_registry = model_registry
        self._prompt_registry = prompt_registry

    async def _resolve_versions(self, state: ComplianceState) -> ComplianceState:
        model_version = DEFAULT_MODEL_VERSION
        prompt_version = DEFAULT_PROMPT_VERSION
        if self._model_registry:
            try:
                record = await self._model_registry.get_model("compliance-model")
                if record:
                    model_version = f"{record.model_name}@{record.version}"
            except Exception:  # noqa: S110
                pass
        if self._prompt_registry:
            prompt_record = await self._prompt_registry.get_prompt("compliance-prompt")
            if prompt_record:
                prompt_version = prompt_record.version
        if state.model_version != model_version or state.prompt_version != prompt_version:
            return state.transition(model_version=model_version, prompt_version=prompt_version)
        return state

    async def run(self, state: ComplianceState) -> ComplianceState:
        """Run compliance workflow. Return cached state if idempotent hit."""
        if self._store:
            cached = await self._store.get_compliance_state(state.event_id)
            if cached is not None:
                logger.info(
                    "compliance_workflow_idempotent_skip",
                    extra={"event_id": state.event_id, "correlation_id": state.correlation_id},
                )
                return cached

        current = await self._resolve_versions(state)

        if not _node_done_compliance(current, "retrieval"):
            current = await retrieve_context_compliance(current, audit_logger=self._audit)
        if not _node_done_compliance(current, "policy_validation"):
            current = await validate_policy_compliance(current, audit_logger=self._audit)
        if not _node_done_compliance(current, "risk_scoring"):
            current = await score_risk_compliance(current, audit_logger=self._audit)
        if not _node_done_compliance(current, "guardrails"):
            current = await apply_guardrails_compliance(current, audit_logger=self._audit)
        if not _node_done_compliance(current, "decision"):
            current = await make_compliance_decision(current, audit_logger=self._audit)

        if self._store:
            await self._store.set_compliance_state(current.event_id, current)

        return current
