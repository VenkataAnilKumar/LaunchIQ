"""Cognitive ReAct loop with tool execution, reflection, cost budget and call limits.

Production reliability features:
- Mid-loop cost budget enforcement (stops early, returns best text)
- Soft warning at 80% of budget for observability
- Hard max_tool_calls independent of cost
- Structured truncation of tool results
- Retry with backoff on transient API errors
- Optional reflection pass with token accounting
- Structured budget metric events for dashboarding
- Structured tool-call metric events for dashboarding
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from .llm import AgentError, estimate_cost_usd

logger = logging.getLogger(__name__)


def _emit_budget_metric(status: str, estimated_cost_usd: float, budget_usd: float, **extra: Any) -> None:
    """Emit a consistent structured event for cost-budget observability.

    Always logs with metric='cognitive_loop_budget_event' so dashboards/alerts can key on it
    without a dedicated metrics client. Extra fields are merged into the log record.
    """
    payload = {
        "metric": "cognitive_loop_budget_event",
        "budget_status": status,
        "estimated_cost_usd": estimated_cost_usd,
        "budget_usd": budget_usd,
        **extra,
    }
    level = logging.WARNING if status == "exceeded" else logging.INFO
    logger.log(
        level,
        "cognitive_loop_budget_event status=%s estimated_cost_usd=%.4f budget_usd=%.4f",
        status,
        estimated_cost_usd,
        budget_usd,
        extra=payload,
    )


def _emit_tool_metric(status: str, tool_calls_made: int, max_tool_calls: int, **extra: Any) -> None:
    """Emit a consistent structured event for tool-call limit observability.

    Always logs with metric='cognitive_loop_tool_event' so dashboards/alerts can key on it
    without a dedicated metrics client.
    """
    payload = {
        "metric": "cognitive_loop_tool_event",
        "tool_status": status,
        "tool_calls_made": tool_calls_made,
        "max_tool_calls": max_tool_calls,
        **extra,
    }
    level = logging.WARNING if status == "limit_reached" else logging.INFO
    logger.log(
        level,
        "cognitive_loop_tool_event status=%s tool_calls_made=%d max_tool_calls=%d",
        status,
        tool_calls_made,
        max_tool_calls,
        extra=payload,
    )


@dataclass
class LoopConfig:
    max_iterations: int = 10
    enable_reflection: bool = False
    max_api_retries: int = 2
    cost_budget_usd: float | None = None
    max_tool_calls: int = 8  # hard cap independent of cost
    tool_result_char_limit: int = 2000
    tool_timeout_seconds: float = 30.0
    retry_backoff_seconds: float = 1.0
    # Accumulated by the loop
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    tool_calls_made: int = 0


async def run_tool_loop(
    client: Any,
    params: dict[str, Any],
    tool_executor: Any | None = None,
    config: LoopConfig | None = None,
) -> tuple[str, list[dict[str, Any]], str | None]:
    """Run a ReAct-style tool loop. Returns (final_text, tool_log, thinking_text)."""
    cfg = config or LoopConfig()
    messages = list(params.get("messages") or [])
    model = params.get("model", "")
    tool_log: list[dict[str, Any]] = []
    last_text = ""
    thinking: str | None = None

    for iteration in range(cfg.max_iterations):
        # --- API call with retries ---
        response = None
        last_exc: Exception | None = None
        for attempt in range(cfg.max_api_retries + 1):
            try:
                response = await client.messages.create(**params)
                break
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if attempt == cfg.max_api_retries:
                    raise AgentError(f"LLM call failed after retries: {exc}") from exc
                await asyncio.sleep(cfg.retry_backoff_seconds * (2**attempt))
        if response is None:
            raise AgentError("No response from LLM") from last_exc

        # Accumulate tokens and check budget mid-loop
        usage = getattr(response, "usage", None)
        if usage:
            cfg.total_input_tokens += getattr(usage, "input_tokens", 0) or 0
            cfg.total_output_tokens += getattr(usage, "output_tokens", 0) or 0
            if cfg.cost_budget_usd is not None:
                est = estimate_cost_usd(model, cfg.total_input_tokens, cfg.total_output_tokens)
                if est > cfg.cost_budget_usd:
                    _emit_budget_metric("exceeded", est, cfg.cost_budget_usd, iteration=iteration)
                    return last_text or "[stopped: cost budget exceeded]", tool_log, thinking
                elif est > 0.8 * cfg.cost_budget_usd:
                    _emit_budget_metric(
                        "approaching",
                        est,
                        cfg.cost_budget_usd,
                        iteration=iteration,
                        pct=(est / cfg.cost_budget_usd) * 100,
                    )

        # Extract content
        text_parts: list[str] = []
        tool_uses: list[Any] = []
        for block in getattr(response, "content", []) or []:
            btype = getattr(block, "type", None)
            if btype == "text":
                text_parts.append(getattr(block, "text", "") or "")
            elif btype == "tool_use":
                tool_uses.append(block)
            elif btype == "thinking":
                thinking = getattr(block, "thinking", None)

        last_text = "\n".join(t for t in text_parts if t).strip()

        if getattr(response, "stop_reason", None) != "tool_use" or not tool_uses:
            # Done
            if cfg.enable_reflection and last_text:
                last_text = await _maybe_reflect(client, params, last_text, cfg, model)
            return last_text, tool_log, thinking

        # Execute tools
        tool_results: list[dict[str, Any]] = []
        for tu in tool_uses:
            if cfg.tool_calls_made >= cfg.max_tool_calls:
                _emit_tool_metric(
                    "limit_reached",
                    cfg.tool_calls_made,
                    cfg.max_tool_calls,
                    iteration=iteration,
                )
                return last_text or "[stopped: max tool calls reached]", tool_log, thinking

            name = getattr(tu, "name", "unknown")
            inp = getattr(tu, "input", {}) or {}
            tool_id = getattr(tu, "id", "")
            try:
                if tool_executor is None:
                    result: Any = {"error": "no tool executor configured"}
                else:
                    result = await asyncio.wait_for(
                        tool_executor.execute(name, inp),
                        timeout=cfg.tool_timeout_seconds,
                    )
            except Exception as exc:  # noqa: BLE001
                result = {"error": str(exc)}

            truncated = _truncate_tool_result(result, cfg.tool_result_char_limit)
            tool_log.append({"tool_name": name, "input": inp, "output": truncated})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": json.dumps(truncated) if not isinstance(truncated, str) else truncated,
                }
            )
            cfg.tool_calls_made += 1

        # Feed results back
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
        params["messages"] = messages

    logger.warning("max_iterations_reached limit=%d", cfg.max_iterations)
    return last_text, tool_log, thinking


def _truncate_tool_result(result: Any, limit: int = 2000) -> Any:
    """Prefer structured truncation that keeps top-level keys when possible."""
    if result is None:
        return result
    text = json.dumps(result) if not isinstance(result, str) else result
    if len(text) <= limit:
        return result

    if isinstance(result, dict):
        # Keep as many top-level keys as fit
        kept: dict[str, Any] = {}
        original_keys = list(result.keys())
        for k, v in result.items():
            trial = {**kept, k: v}
            if len(json.dumps(trial)) > limit - 200:
                break
            kept[k] = v
        return {
            "truncated": True,
            "original_length": len(text),
            "original_keys": original_keys,
            "kept": kept,
            "note": "truncated to fit context",
        }

    # Fallback string preview
    return {
        "truncated": True,
        "original_length": len(text),
        "preview": text[: limit - 100] + "...",
    }


async def _maybe_reflect(
    client: Any,
    params: dict[str, Any],
    text: str,
    cfg: LoopConfig,
    model: str,
) -> str:
    """Optional short reflection pass. Accumulates tokens and re-checks budget."""
    if not text or not cfg.enable_reflection:
        return text

    reflection_prompt = (
        "You are reviewing the previous response for accuracy, completeness, and grounding. "
        "If it is already high quality, reply with the original text unchanged. "
        "Otherwise, provide a concise improved version. Do not add new facts."
    )
    reflect_messages = [
        {"role": "user", "content": f"{reflection_prompt}\n\nOriginal response:\n{text[:2000]}"},
    ]
    reflect_params = {
        "model": params.get("model", model),
        "messages": reflect_messages,
        "max_tokens": 800,
    }

    try:
        response = await client.messages.create(**reflect_params)
        usage = getattr(response, "usage", None)
        if usage:
            cfg.total_input_tokens += getattr(usage, "input_tokens", 0) or 0
            cfg.total_output_tokens += getattr(usage, "output_tokens", 0) or 0
            if cfg.cost_budget_usd is not None:
                est = estimate_cost_usd(model, cfg.total_input_tokens, cfg.total_output_tokens)
                if est > cfg.cost_budget_usd:
                    _emit_budget_metric("exceeded", est, cfg.cost_budget_usd, phase="reflection")
                    return text  # keep original; do not use potentially over-budget reflection

        text_parts: list[str] = []
        for block in getattr(response, "content", []) or []:
            if getattr(block, "type", None) == "text":
                text_parts.append(getattr(block, "text", "") or "")
        refined = "\n".join(t for t in text_parts if t).strip()
        if refined:
            logger.info(
                "reflection_applied original_chars=%d refined_chars=%d",
                len(text),
                len(refined),
                extra={"phase": "reflection", "tokens_added": True},
            )
            return refined
    except Exception as exc:  # noqa: BLE001
        logger.warning("reflection_failed falling_back_to_original: %s", exc)

    return text
