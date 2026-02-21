"""Risk workflow: LangGraph-style orchestration — retrieval → policy → scoring → guardrails → decision."""

import logging
from typing import Optional

from app.governance.audit_logger import AuditLogger
from app.governance.model_registry import ModelRegistry
from app.governance.prompt_registry import PromptRegistry
from app.workflows.langgraph.nodes.decision import make_decision
from app.workflows.langgraph.nodes.guardrails import apply_guardrails
from app.workflows.langgraph.nodes.policy_validation import validate_policy
from app.workflows.langgraph.nodes.retrieval import retrieve_context
from app.workflows.langgraph.nodes.risk_scoring import score_risk
from app.workflows.langgraph.state_models import RiskState
from app.workflows.langgraph.workflow_state_store import WorkflowStateStore

logger = logging.getLogger(__name__)

DEFAULT_MODEL_VERSION = "simulated@1"
DEFAULT_PROMPT_VERSION = 1
NODE_ORDER = ["retrieval", "policy_validation", "risk_scoring", "guardrails", "decision"]


def _node_done(state: RiskState, node: str) -> bool:
    """True if audit_trail shows this node already executed."""
    return any((e.get("node") == node for e in state.audit_trail))


class RiskWorkflow:
    """
    Orchestrated risk workflow. Idempotent: if state cached for event_id, return it.
    Otherwise run: retrieval → policy_validation → risk_scoring → guardrails → decision.
    Deterministic; no randomness. Emits audit at each stage; logs model and prompt version.
    """

    def __init__(
        self,
        audit_logger: AuditLogger,
        state_store: Optional[WorkflowStateStore] = None,
        model_registry: Optional[ModelRegistry] = None,
        prompt_registry: Optional[PromptRegistry] = None,
    ) -> None:
        self._audit = audit_logger
        self._store = state_store
        self._model_registry = model_registry
        self._prompt_registry = prompt_registry

    async def _resolve_versions(self, state: RiskState) -> RiskState:
        """Set model_version and prompt_version from registries if available."""
        model_version = DEFAULT_MODEL_VERSION
        prompt_version = DEFAULT_PROMPT_VERSION
        if self._model_registry:
            try:
                record = await self._model_registry.get_model("risk-model")
                if record:
                    model_version = f"{record.model_name}@{record.version}"
            except Exception:  # noqa: S110
                pass
        if self._prompt_registry:
            prompt_record = await self._prompt_registry.get_prompt("risk-prompt")
            if prompt_record:
                prompt_version = prompt_record.version
        if state.model_version != model_version or state.prompt_version != prompt_version:
            return state.transition(model_version=model_version, prompt_version=prompt_version)
        return state

    async def run(self, state: RiskState) -> RiskState:
        """
        Run workflow. If state_store has cached state for this event_id, return it (idempotent).
        Otherwise run each node in order, skipping any already in audit_trail; then cache and return.
        """
        if self._store:
            cached = await self._store.get_risk_state(state.event_id)
            if cached is not None:
                logger.info(
                    "workflow_idempotent_skip",
                    extra={"event_id": state.event_id, "correlation_id": state.correlation_id},
                )
                return cached

        current = await self._resolve_versions(state)

        if not _node_done(current, "retrieval"):
            current = await retrieve_context(current, audit_logger=self._audit)
        if not _node_done(current, "policy_validation"):
            current = await validate_policy(current, audit_logger=self._audit)
        if not _node_done(current, "risk_scoring"):
            current = await score_risk(current, audit_logger=self._audit)
        if not _node_done(current, "guardrails"):
            current = await apply_guardrails(current, audit_logger=self._audit)
        if not _node_done(current, "decision"):
            current = await make_decision(current, audit_logger=self._audit)

        if self._store:
            await self._store.set_risk_state(current.event_id, current)

        return current
