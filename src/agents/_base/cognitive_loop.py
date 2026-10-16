"""
Cognitive loop — Perceive → Reason → Act → Validate → Reflect.

Implements the agentic tool-use loop: calls Claude, handles tool_use
blocks, executes tools, feeds results back, repeats until stop_reason
is 'end_turn' or max_iterations reached.

Optional reflection step (when LoopConfig.enable_reflection=True) injects
a brief self-critique before the final return to improve output quality
without changing the public contract.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

import anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LoopConfig(BaseModel):
    max_iterations: int = 10
    enable_reflection: bool = True


class CognitiveLoop:
    def __init__(self, config: LoopConfig) -> None:
        self.config = config


async def run_tool_loop(
    client: anthropic.Anthropic,
    params: dict[str, Any],
    tool_executor: Any | None,
    config: LoopConfig | None = None,
) -> tuple[str, list[dict[str, Any]], str | None]:
    """
    Core ReAct loop with optional reflection.

    Returns:
        final_text   — concatenated text from the final message
        tool_log     — list of {tool_name, input, output} dicts
        thinking_text — extended thinking content or None
    """
    cfg = config or LoopConfig()
    messages: list[dict[str, Any]] = list(params.get("messages", []))
    tool_log: list[dict[str, Any]] = []
    thinking_text: str | None = None
    max_iters = params.pop("_max_iterations", cfg.max_iterations)

    for iteration in range(max_iters):
        iter_start = time.perf_counter()
        call_params = {**params, "messages": messages}
        response = client.messages.create(**call_params)
        iter_ms = int((time.perf_counter() - iter_start) * 1000)

        # Collect thinking blocks
        for block in response.content:
            if block.type == "thinking":
                thinking_text = block.thinking

        # Collect text + check stop reason
        text_parts = [b.text for b in response.content if b.type == "text"]
        final_text = "".join(text_parts)

        tool_count = sum(1 for b in response.content if b.type == "tool_use")
        logger.info(
            "Cognitive loop iter=%d stop=%s tools=%d latency_ms=%d",
            iteration,
            response.stop_reason,
            tool_count,
            iter_ms,
        )

        if response.stop_reason == "end_turn":
            if cfg.enable_reflection and iteration > 0 and final_text:
                final_text = await _maybe_reflect(client, params, messages, final_text)
            return final_text, tool_log, thinking_text

        if response.stop_reason != "tool_use" or tool_executor is None:
            return final_text, tool_log, thinking_text

        # --- Execute tool calls ---
        tool_results: list[dict[str, Any]] = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            logger.debug("Tool call: %s %s", block.name, block.input)
            try:
                result = await tool_executor.execute(block.name, block.input)
            except Exception as exc:
                logger.warning("Tool %s failed: %s", block.name, exc)
                result = {"error": str(exc)}

            tool_log.append({"tool_name": block.name, "input": block.input, "output": result})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                }
            )

        # Feed results back into the conversation
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    logger.warning("Cognitive loop hit max_iterations — returning last text")
    return final_text, tool_log, thinking_text


async def _maybe_reflect(
    client: anthropic.Anthropic,
    params: dict[str, Any],
    messages: list[dict[str, Any]],
    current_text: str,
) -> str:
    """Optional lightweight reflection to tighten final answer."""
    reflect_messages = messages + [
        {
            "role": "user",
            "content": (
                "Briefly critique the previous answer for completeness, accuracy, "
                "and clarity. Then provide an improved final version. "
                "Return ONLY the improved answer."
            ),
        }
    ]
    try:
        reflect_params = {**params, "messages": reflect_messages, "max_tokens": params.get("max_tokens", 1024)}
        response = client.messages.create(**reflect_params)
        improved = "".join(b.text for b in response.content if b.type == "text")
        return improved.strip() or current_text
    except Exception as exc:
        logger.debug("Reflection skipped: %s", exc)
        return current_text
