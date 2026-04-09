"""Base agent class — all LaunchIQ agents inherit from this."""
from __future__ import annotations

import abc
import logging
from typing import Any, AsyncIterator

import anthropic
from pydantic import BaseModel

from .cognitive_loop import CognitiveLoop, LoopConfig
from .context_builder import ContextBuilder
from .output_validator import OutputValidator

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    agent_id: str
    model: str = "claude-sonnet-4-6"
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
        self.client = anthropic.Anthropic()
        self.loop = CognitiveLoop(LoopConfig(max_iterations=10, enable_reflection=True))
        self.context_builder = ContextBuilder()
        self.validator = OutputValidator()
        self._logger = logging.getLogger(f"agent.{config.agent_id}")

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
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "system": self.config.system_prompt,
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
    ) -> tuple[str, list[dict[str, Any]], str | None]:
        """
        Agentic loop: call Claude, execute tools, feed results back.
        Returns (final_text, tool_call_log, thinking_text).
        """
        from .cognitive_loop import run_tool_loop

        params = self._make_api_params(messages)
        params["_max_iterations"] = self.loop.config.max_iterations
        return await run_tool_loop(self.client, params, tool_executor)

    def _validate_output(self, raw: dict[str, Any]) -> dict[str, Any]:
        schema = self.get_output_schema()
        return self.validator.validate(raw, schema)

    def _check_hitl(self, output: dict[str, Any]) -> tuple[bool, str | None]:
        """Override in agents that have HITL checkpoints."""
        return False, None
