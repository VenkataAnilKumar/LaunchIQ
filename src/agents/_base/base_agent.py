"""Base agent class — all LaunchIQ agents inherit from this."""
from __future__ import annotations

import abc
import logging
from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel

from .cognitive_loop import CognitiveLoop, LoopConfig
from .context_builder import ContextBuilder
from .llm import AgentError, estimate_cost_usd, extract_json, get_client, resolve_model
from .output_validator import OutputValidator
from .prompts import SAFETY_RULES

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    agent_id: str
    # A literal model id, or a tier alias: "opus" | "sonnet" | "haiku" (resolved from settings).
    model: str = "sonnet"
    max_tokens: int = 8192
    temperature: float = 1.0  # required for extended thinking
    enable_thinking: bool = False
    thinking_budget: int = 5000
    tools: list[dict[str, Any]] = []
    system_prompt: str = ""


class AgentResult(BaseModel):
    agent_id: str
    output: dict[str, Any]
    thinking: str | None = None
    tool_calls: list[dict[str, Any]] = []
    tokens_used: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    hitl_required: bool = False
    hitl_checkpoint: str | None = None


class BaseAgent(abc.ABC):
    """
    Foundation for all LaunchIQ agents.

    Architecture (2026 pattern):
      - Cognitive loop: Perceive → Reason → Act → Validate → Reflect
      - Tool execution gate: scope check + param validation before every call
      - Output gate: Pydantic schema + hallucination check after every response
      - HITL hooks: structural pause/resume — not a UX layer
    """

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        # Reflection rewrites free text and can corrupt structured JSON, so it is opt-in.
        self.loop = CognitiveLoop(LoopConfig(max_iterations=10, enable_reflection=False))
        self._input_tokens = 0
        self._output_tokens = 0
        self.context_builder = ContextBuilder()
        self.validator = OutputValidator()
        self._logger = logging.getLogger(f"agent.{config.agent_id}")

    @property
    def client(self) -> Any:
        """Async LLM client (created lazily so importing never needs an API key)."""
        return get_client()

    @property
    def model_id(self) -> str:
        return resolve_model(self.config.model)

    def usage_snapshot(self) -> dict[str, Any]:
        """Token/cost totals across every model call this agent instance has made."""
        return {
            "input_tokens": self._input_tokens,
            "output_tokens": self._output_tokens,
            "tokens_used": self._input_tokens + self._output_tokens,
            "cost_usd": estimate_cost_usd(self.model_id, self._input_tokens, self._output_tokens),
        }

    def make_result(self, output: dict[str, Any], **extra: Any) -> AgentResult:
        """Build an AgentResult carrying this instance's usage totals."""
        usage = self.usage_snapshot()
        return AgentResult(agent_id=self.config.agent_id, output=output, **usage, **extra)

    # ------------------------------------------------------------------ #
    # Abstract interface — each agent implements these                     #
    # ------------------------------------------------------------------ #

    @abc.abstractmethod
    async def run(self, payload: dict[str, Any]) -> AgentResult:
        """Entry point called by the orchestrator or Lambda handler."""
        ...

    @abc.abstractmethod
    async def stream(self, payload: dict[str, Any]) -> AsyncIterator[str]:
        """SSE streaming variant — yields delta text chunks."""
        ...

    @abc.abstractmethod
    def get_output_schema(self) -> type[BaseModel]:
        """Return the Pydantic model this agent's output must conform to."""
        ...

    # ------------------------------------------------------------------ #
    # Shared helpers                                                       #
    # ------------------------------------------------------------------ #

    def _build_messages(
        self,
        user_content: str,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Construct the messages list, injecting retrieved context."""
        messages: list[dict[str, Any]] = []
        if context:
            enriched = self.context_builder.inject(user_content, context)
            messages.append({"role": "user", "content": enriched})
        else:
            messages.append({"role": "user", "content": user_content})
        return messages

    def _make_api_params(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        params: dict[str, Any] = {
            "model": self.model_id,
            "max_tokens": self.config.max_tokens,
            "system": f"{self.config.system_prompt}{SAFETY_RULES}",
            "messages": messages,
        }
        if self.config.tools:
            params["tools"] = self.config.tools
        if self.config.enable_thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.config.thinking_budget,
            }
            params["temperature"] = 1.0
        return params

    async def _call_with_tools(
        self,
        messages: list[dict[str, Any]],
        tool_executor: Any | None = None,
        **param_overrides: Any,
    ) -> tuple[str, list[dict[str, Any]], str | None]:
        """
        Agentic loop: call Claude, execute tools, feed results back.
        Returns (final_text, tool_call_log, thinking_text). Raises AgentError on
        permanent API failure. Token usage accumulates on the agent instance.
        """
        from .cognitive_loop import run_tool_loop

        base = self.loop.config
        cfg = LoopConfig(
            max_iterations=base.max_iterations,
            enable_reflection=base.enable_reflection,
            max_api_retries=base.max_api_retries,
            cost_budget_usd=base.cost_budget_usd,
            tool_result_char_limit=base.tool_result_char_limit,
            tool_timeout_seconds=base.tool_timeout_seconds,
            retry_backoff_seconds=base.retry_backoff_seconds,
        )
        params = self._make_api_params(messages)
        params.update(param_overrides)
        params["_max_iterations"] = cfg.max_iterations
        try:
            return await run_tool_loop(self.client, params, tool_executor, config=cfg)
        finally:
            self._input_tokens += cfg.total_input_tokens
            self._output_tokens += cfg.total_output_tokens

    async def _generate_validated(
        self,
        messages: list[dict[str, Any]],
        tool_executor: Any | None = None,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], str | None]:
        """Call the model, parse JSON and validate against the output schema.

        On a parse/schema failure the model gets one chance to repair its answer
        with the validation error fed back. Returns (validated, tool_calls, thinking).
        """
        text, tool_calls, thinking = await self._call_with_tools(messages, tool_executor)
        try:
            return self._validate_output(extract_json(text)), tool_calls, thinking
        except (AgentError, ValueError) as first_error:
            self._logger.warning("Output invalid, attempting one repair: %s", first_error)
            repair = [
                *messages,
                {"role": "assistant", "content": text or "(empty)"},
                {
                    "role": "user",
                    "content": (
                        "Your previous answer could not be used: "
                        f"{str(first_error)[:800]}\n"
                        "Reply again with ONLY the corrected JSON object."
                    ),
                },
            ]
            text, more_calls, thinking2 = await self._call_with_tools(repair, None)
            try:
                validated = self._validate_output(extract_json(text))
            except ValueError as exc:
                raise AgentError(f"{self.config.agent_id} produced invalid output: {exc}") from exc
            return validated, [*tool_calls, *more_calls], thinking2 or thinking

    @staticmethod
    def _brief_block(payload: dict[str, Any]) -> str:
        """Render the launch brief so every agent sees the same product facts."""
        competitors = payload.get("competitors") or []
        return (
            "<launch_brief>\n"
            f"product_name: {payload.get('product_name', '')}\n"
            f"description: {payload.get('description', '')}\n"
            f"target_market: {payload.get('target_market', '')}\n"
            f"competitors: {', '.join(competitors) if competitors else 'none given'}\n"
            f"launch_date: {payload.get('launch_date') or 'unspecified'}\n"
            "</launch_brief>\n"
        )

    def _validate_output(self, raw: dict[str, Any]) -> dict[str, Any]:
        schema = self.get_output_schema()
        return self.validator.validate(raw, schema)

    def _check_hitl(self, output: dict[str, Any]) -> tuple[bool, str | None]:
        """Override in agents that have HITL checkpoints."""
        return False, None
