"""
Cognitive loop — Perceive → Reason → Act → Validate → Reflect.

Implements the agentic tool-use loop: calls Claude, handles tool_use
blocks, executes tools, feeds results back, repeats until stop_reason
is 'end_turn' or max_iterations reached.

Optional reflection step (when LoopConfig.enable_reflection=True) injects
a brief self-critique before the final return to improve output quality
without changing the public contract.

Tool results are truncated to a soft character limit before being fed back
to prevent context window bloat from large tool/RAG payloads.

API calls are retried once (configurable) on transient failures for better
reliability under rate limits or provider blips.

Token usage (input/output) is accumulated across iterations and logged on
completion for cost observability. A rough USD cost estimate (Sonnet-class rates)
is also logged. Total loop latency is accumulated and logged. Optional cost_budget_usd
emits a warning if the estimate exceeds the budget. Tool execution errors are counted
and included in completion logs for reliability observability.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

import anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Soft limit on tool result size (characters) to protect context window.
_MAX_TOOL_RESULT_CHARS = 2000

# Approximate Sonnet-4.6 rates for cost observability (USD per million tokens).
_INPUT_COST_PER_MTOK = 3.0
_OUTPUT_COST_PER_MTOK = 15.0


class LoopConfig(BaseModel):
    max_iterations: int = 10
    enable_reflection: bool = True
    max_api_retries: int = 1
    cost_budget_usd: float | None = None  # optional soft budget for warning


class CognitiveLoop:
    def __init__(self, config: LoopConfig) -> None:
        self.config = config


def _truncate_tool_result(result: Any, max_chars: int = _MAX_TOOL_RESULT_CHARS) -> Any:
    """Truncate large tool results to keep conversation context bounded."""
    try:
        serialized = json.dumps(result)
        if len(serialized) <= max_chars:
            return result
        # Truncate the serialized form and re-wrap as a dict with a note
        truncated = serialized[: max_chars - 30] + "... [truncated]"
        return {"truncated": True, "content": truncated, "original_length": len(serialized)}
    except Exception:
        return result


def _estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    """Rough cost estimate using Sonnet-class rates. For observability only."""
    input_cost = (input_tokens / 1_000_000) * _INPUT_COST_PER_MTOK
    output_cost = (output_tokens / 1_000_000) * _OUTPUT_COST_PER_MTOK
    return round(input_cost + output_cost, 6)


async def _call_with_retry(
    client: anthropic.Anthropic,
    params: dict[str, Any],
    max_retries: int,
) -> Any:
    """Call messages.create with simple exponential-ish backoff on failure."""
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return client.messages.create(**params)
        except Exception as exc:
            last_exc = exc
            if attempt >= max_retries:
                break
            wait = 0.4 * (attempt + 1)
            logger.warning(
                "Claude API call failed (attempt %d/%d): %s — retrying in %.1fs",
                attempt + 1,
                max_retries + 1,
                exc,
                wait,
            )
            await asyncio.sleep(wait)
    logger.error("Claude API call failed after %d retries: %s", max_retries, last_exc)
    raise last_exc if last_exc else RuntimeError("API call failed")


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
    last_tool_count = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_latency_ms = 0
    tool_error_count = 0

    for iteration in range(max_iters):
        iter_start = time.perf_counter()
        call_params = {**params, "messages": messages}
        response = await _call_with_retry(client, call_params, cfg.max_api_retries)
        iter_ms = int((time.perf_counter() - iter_start) * 1000)
        total_latency_ms += iter_ms

        # Accumulate token usage when available (Anthropic Message.usage)
        usage = getattr(response, "usage", None)
        if usage is not None:
            total_input_tokens += getattr(usage, "input_tokens", 0) or 0
            total_output_tokens += getattr(usage, "output_tokens", 0) or 0

        # Collect thinking blocks
        for block in response.content:
            if block.type == "thinking":
                thinking_text = block.thinking

        # Collect text + check stop reason
        text_parts = [b.text for b in response.content if b.type == "text"]
        final_text = "".join(text_parts)

        tool_count = sum(1 for b in response.content if b.type == "tool_use")
        last_tool_count = tool_count
        logger.info(
            "Cognitive loop iter=%d stop=%s tools=%d latency_ms=%d",
            iteration,
            response.stop_reason,
            tool_count,
            iter_ms,
        )

        if response.stop_reason == "end_turn":
            if cfg.enable_reflection and iteration > 0 and final_text:
                improved = await _maybe_reflect(client, params, messages, final_text)
                if improved and improved != final_text:
                    logger.info("Reflection improved final answer (len %d -> %d)", len(final_text), len(improved))
                    final_text = improved
            est_cost = _estimate_cost_usd(total_input_tokens, total_output_tokens)
            if cfg.cost_budget_usd is not None and est_cost > cfg.cost_budget_usd:
                logger.warning(
                    "Cognitive loop cost estimate %.6f USD exceeds budget %.6f USD",
                    est_cost,
                    cfg.cost_budget_usd,
                )
            logger.info(
                "Cognitive loop complete: input_tokens=%d output_tokens=%d est_cost_usd=%.6f total_latency_ms=%d iterations=%d tool_errors=%d",
                total_input_tokens,
                total_output_tokens,
                est_cost,
                total_latency_ms,
                iteration + 1,
                tool_error_count,
            )
            return final_text, tool_log, thinking_text

        if response.stop_reason != "tool_use" or tool_executor is None:
            est_cost = _estimate_cost_usd(total_input_tokens, total_output_tokens)
            if cfg.cost_budget_usd is not None and est_cost > cfg.cost_budget_usd:
                logger.warning(
                    "Cognitive loop cost estimate %.6f USD exceeds budget %.6f USD",
                    est_cost,
                    cfg.cost_budget_usd,
                )
            logger.info(
                "Cognitive loop complete: input_tokens=%d output_tokens=%d est_cost_usd=%.6f total_latency_ms=%d iterations=%d tool_errors=%d",
                total_input_tokens,
                total_output_tokens,
                est_cost,
                total_latency_ms,
                iteration + 1,
                tool_error_count,
            )
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
                tool_error_count += 1

            # Truncate large results before feeding back
            result = _truncate_tool_result(result)

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

    est_cost = _estimate_cost_usd(total_input_tokens, total_output_tokens)
    if cfg.cost_budget_usd is not None and est_cost > cfg.cost_budget_usd:
        logger.warning(
            "Cognitive loop cost estimate %.6f USD exceeds budget %.6f USD",
            est_cost,
            cfg.cost_budget_usd,
        )
    logger.warning(
        "Cognitive loop hit max_iterations=%d — returning last text (last_tool_count=%d, total_tools_logged=%d, tool_errors=%d, input_tokens=%d, output_tokens=%d, est_cost_usd=%.6f, total_latency_ms=%d)",
        max_iters,
        last_tool_count,
        len(tool_log),
        tool_error_count,
        total_input_tokens,
        total_output_tokens,
        est_cost,
        total_latency_ms,
    )
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
        response = await _call_with_retry(client, reflect_params, 0)  # no extra retry on reflection
        improved = "".join(b.text for b in response.content if b.type == "text")
        return improved.strip() or current_text
    except Exception as exc:
        logger.debug("Reflection skipped: %s", exc)
        return current_text
