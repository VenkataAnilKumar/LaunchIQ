"""
Cognitive loop — Perceive → Reason → Act → Validate → Reflect.

Implements the agentic tool-use loop: calls Claude, handles tool_use
blocks, executes tools, feeds results back, repeats until stop_reason
is 'end_turn' or max_iterations reached.
"""
from __future__ import annotations

import json
import logging
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
) -> tuple[str, list[dict[str, Any]], str | None]:
    """
    Core ReAct loop.

    Returns:
        final_text   — concatenated text from the final message
        tool_log     — list of {tool_name, input, output} dicts
        thinking_text — extended thinking content or None
    """
    messages: list[dict[str, Any]] = list(params.get("messages", []))
    tool_log: list[dict[str, Any]] = []
    thinking_text: str | None = None

    for iteration in range(params.pop("_max_iterations", 10)):
        call_params = {**params, "messages": messages}
        response = client.messages.create(**call_params)

        # Collect thinking blocks
        for block in response.content:
            if block.type == "thinking":
                thinking_text = block.thinking

        # Collect text + check stop reason
        text_parts = [b.text for b in response.content if b.type == "text"]
        final_text = "".join(text_parts)

        if response.stop_reason == "end_turn":
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
