"""
CognitiveLoop — ReAct + optional reflection tool loop for LaunchIQ agents.

Implements the Perceive → Reason → Act → Validate → Reflect cycle with:
- Tool execution (with error isolation and optional timeout)
- Soft truncation of large tool results (configurable limit)
- Configurable API retries for transient failures
- Token / latency / tool-success observability logging
- Optional post-generation reflection pass

Public surface:
  - LoopConfig
  - CognitiveLoop
  - run_tool_loop(...)
  - _truncate_tool_result
  - _maybe_reflect (internal, patchable)
"""
from __future__ import annotations

import asyncio
import inspect
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from .llm import AgentError, estimate_cost_usd

logger = logging.getLogger(__name__)

# Soft character limit for tool results fed back into the model.
_TOOL_RESULT_CHAR_LIMIT = 2000

# Approximate Sonnet-class pricing (USD per million tokens) for rough cost estimates.
_INPUT_COST_PER_MTOK = 3.0
_OUTPUT_COST_PER_MTOK = 15.0


@dataclass
class LoopConfig:
    """Configuration for a cognitive tool loop."""

    max_iterations: int = 10
    enable_reflection: bool = True
    max_api_retries: int = 1
    cost_budget_usd: float | None = None
    tool_result_char_limit: int = 2000
    tool_timeout_seconds: float | None = None
    # Seconds to wait before an API retry (doubles each attempt).
    retry_backoff_seconds: float = 0.5
    # Model used for the optional reflection pass (defaults to the main call's model).
    reflection_model: str | None = None
    # Internal counters (populated during run; useful for tests / callers)
    total_tool_calls: int = 0
    tool_error_count: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_latency_ms: int = 0


class CognitiveLoop:
    """Thin wrapper that holds config and exposes the run entrypoint."""

    def __init__(self, config: LoopConfig | None = None) -> None:
        self.config = config or LoopConfig()

    async def run(
        self,
        client: Any,
        params: dict[str, Any],
        tool_executor: Any | None = None,
    ) -> tuple[str, list[dict[str, Any]], str | None]:
        return await run_tool_loop(client, params, tool_executor, config=self.config)


def _estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Rough USD cost using Sonnet-class rates. Never raises."""
    return round(
        (input_tokens / 1_000_000) * _INPUT_COST_PER_MTOK
        + (output_tokens / 1_000_000) * _OUTPUT_COST_PER_MTOK,
        6,
    )


def _truncate_tool_result(result: Any, limit: int = _TOOL_RESULT_CHAR_LIMIT) -> Any:
    """Truncate large tool results so they don't bloat the context window.

    Small results pass through unchanged. Large dicts/strings are replaced with a
    truncated marker that preserves the original length for debugging.
    """
    try:
        if isinstance(result, str):
            if len(result) <= limit:
                return result
            return {
                "truncated": True,
                "original_length": len(result),
                "preview": result[: limit - 80] + "...",
            }
        # Serialize once to measure size
        serialized = json.dumps(result, default=str)
        if len(serialized) <= limit:
            return result
        return {
            "truncated": True,
            "original_length": len(serialized),
            "preview": serialized[: limit - 80] + "...",
        }
    except Exception:  # noqa: BLE001 - boundary: tool/reflection failures must not crash the loop
        # Fail open: return original if we cannot measure/truncate
        return result


async def _maybe_reflect(
    client: Any,
    final_text: str,
    messages: list[dict[str, Any]],
    config: LoopConfig,
) -> str:
    """Optional reflection pass. Returns improved text or the original.

    This is a soft, best-effort step. Failures are logged and ignored so the
    primary answer is never blocked.
    """
    if not config.enable_reflection or not final_text.strip():
        return final_text
    try:
        reflect_prompt = (
            "Review the following draft for factual accuracy, completeness, and clarity. "
            "If you can improve it without inventing facts, return the improved version. "
            "Otherwise return the original unchanged.\n\n"
            f"DRAFT:\n{final_text}"
        )
        pending = client.messages.create(
            model=config.reflection_model or "claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": reflect_prompt}],
        )
        resp = await pending if inspect.isawaitable(pending) else pending
        improved = ""
        for block in getattr(resp, "content", []) or []:
            if getattr(block, "type", None) == "text":
                improved = getattr(block, "text", "") or ""
                break
        if improved and improved.strip() and improved != final_text:
            logger.info("CognitiveLoop reflection improved the draft (len %d -> %d)", len(final_text), len(improved))
            return improved
        return final_text
    except Exception as exc:  # noqa: BLE001 - boundary: tool/reflection failures must not crash the loop
        logger.warning("Reflection pass failed (non-fatal): %s", exc)
        return final_text


async def run_tool_loop(
    client: Any,
    params: dict[str, Any],
    tool_executor: Any | None = None,
    config: LoopConfig | None = None,
) -> tuple[str, list[dict[str, Any]], str | None]:
    """
    Execute a ReAct-style tool loop against an Anthropic-compatible client.

    Returns:
        (final_text, tool_call_log, thinking_text)

    Observability (logged, non-blocking):
        - total tokens, rough cost, total latency, tool call count, tool error rate
        - avg latency per iteration, tool success rate
    """
    cfg = config or LoopConfig()
    # Allow callers to override max iterations via params (legacy compatibility)
    max_iters = int(params.pop("_max_iterations", cfg.max_iterations))
    messages = list(params.get("messages") or [])
    tool_log: list[dict[str, Any]] = []
    final_text = ""
    thinking_text: str | None = None

    start_ns = time.perf_counter_ns()
    iteration = 0
    truncation_retries = 0
    stop_reason = None

    while iteration < max_iters:
        iteration += 1
        iter_start = time.perf_counter_ns()

        # --- API call with retry/backoff -------------------------------------------------
        response = None
        for attempt in range(cfg.max_api_retries + 1):
            try:
                pending = client.messages.create(**params)
                response = await pending if inspect.isawaitable(pending) else pending
                break
            except Exception as exc:
                logger.warning(
                    "CognitiveLoop API call failed (attempt %d/%d): %s",
                    attempt + 1,
                    cfg.max_api_retries + 1,
                    exc,
                )
                status = getattr(exc, "status_code", None)
                permanent = isinstance(status, int) and 400 <= status < 500 and status not in (408, 409, 429)
                if attempt == cfg.max_api_retries or permanent:
                    logger.error("CognitiveLoop API call failed permanently")
                    raise AgentError(f"LLM API call failed: {exc}") from exc
                await asyncio.sleep(cfg.retry_backoff_seconds * (2**attempt))
        assert response is not None

        # --- Token / usage accounting ---------------------------------------------------
        usage = getattr(response, "usage", None)
        if usage:
            cfg.total_input_tokens += int(getattr(usage, "input_tokens", 0) or 0)
            cfg.total_output_tokens += int(getattr(usage, "output_tokens", 0) or 0)

        # --- Extract text / thinking ----------------------------------------------------
        text_parts: list[str] = []
        tool_uses: list[Any] = []
        for block in getattr(response, "content", []) or []:
            btype = getattr(block, "type", None)
            if btype == "text":
                text_parts.append(getattr(block, "text", "") or "")
            elif btype == "thinking":
                thinking_text = getattr(block, "thinking", None) or thinking_text
            elif btype == "tool_use":
                tool_uses.append(block)

        if text_parts:
            final_text = "".join(text_parts)

        stop_reason = getattr(response, "stop_reason", None)

        # --- Output cut off by max_tokens: retry once with a larger budget -------------
        if stop_reason == "max_tokens" and not tool_uses:
            current = int(params.get("max_tokens", 0) or 0)
            if truncation_retries < 1 and 0 < current < 32000:
                truncation_retries += 1
                params["max_tokens"] = min(current * 2, 32000)
                logger.warning("Output truncated at max_tokens=%d; retrying with %d", current, params["max_tokens"])
                cfg.total_latency_ms += int((time.perf_counter_ns() - iter_start) / 1_000_000)
                iteration -= 1
                continue
            raise AgentError("Model output was truncated (max_tokens reached)")

        # --- Tool execution -------------------------------------------------------------
        if stop_reason == "tool_use" and tool_uses and tool_executor is not None:
            tool_results = []
            for tu in tool_uses:
                cfg.total_tool_calls += 1
                name = getattr(tu, "name", "unknown")
                inp = getattr(tu, "input", {}) or {}
                tool_id = getattr(tu, "id", None)
                try:
                    if hasattr(tool_executor, "execute"):
                        raw_coro = tool_executor.execute(name, inp)
                    else:
                        raw_coro = tool_executor(name, inp)
                    if cfg.tool_timeout_seconds is not None:
                        raw = await asyncio.wait_for(raw_coro, timeout=cfg.tool_timeout_seconds)
                    else:
                        raw = await raw_coro
                    truncated = _truncate_tool_result(raw, limit=cfg.tool_result_char_limit)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": json.dumps(truncated, default=str) if not isinstance(truncated, str) else truncated,
                    })
                    tool_log.append({"tool_name": name, "input": inp, "output": truncated})
                except TimeoutError:
                    cfg.tool_error_count += 1
                    err_payload = {"error": f"tool timeout after {cfg.tool_timeout_seconds}s"}
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": json.dumps(err_payload),
                        "is_error": True,
                    })
                    tool_log.append({"tool_name": name, "input": inp, "output": err_payload})
                    logger.warning("Tool %s timed out after %.1fs", name, cfg.tool_timeout_seconds or 0)
                except Exception as exc:  # noqa: BLE001 - boundary: tool/reflection failures must not crash the loop
                    cfg.tool_error_count += 1
                    err_payload = {"error": str(exc)}
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": json.dumps(err_payload),
                        "is_error": True,
                    })
                    tool_log.append({"tool_name": name, "input": inp, "output": err_payload})
                    logger.warning("Tool %s failed: %s", name, exc)

            # Feed results back
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            params["messages"] = messages
            # Continue loop
            cfg.total_latency_ms += int((time.perf_counter_ns() - iter_start) / 1_000_000)
            continue

        # end_turn or no more tools
        cfg.total_latency_ms += int((time.perf_counter_ns() - iter_start) / 1_000_000)
        break

    # Max-iteration path
    if iteration >= max_iters and stop_reason == "tool_use":
        logger.warning(
            "CognitiveLoop hit max_iterations=%d (last_tool_count=%d)",
            max_iters,
            len(tool_log),
        )

    # Optional reflection
    if cfg.enable_reflection and final_text:
        cfg.reflection_model = cfg.reflection_model or params.get("model")
        final_text = await _maybe_reflect(client, final_text, messages, cfg)

    # --- Observability logging ----------------------------------------------------------
    total_ms = int((time.perf_counter_ns() - start_ns) / 1_000_000)
    avg_latency = int(cfg.total_latency_ms / max(iteration, 1))
    tool_success_rate = 1.0 - (cfg.tool_error_count / max(cfg.total_tool_calls, 1))
    est_cost = estimate_cost_usd(
        str(params.get("model", "")), cfg.total_input_tokens, cfg.total_output_tokens
    )

    log_payload = {
        "iterations": iteration,
        "total_tool_calls": cfg.total_tool_calls,
        "tool_error_count": cfg.tool_error_count,
        "tool_success_rate": round(tool_success_rate, 3),
        "total_input_tokens": cfg.total_input_tokens,
        "total_output_tokens": cfg.total_output_tokens,
        "estimated_cost_usd": est_cost,
        "total_latency_ms": total_ms,
        "avg_latency_per_iter_ms": avg_latency,
    }
    logger.info("CognitiveLoop completed: %s", log_payload)

    if cfg.cost_budget_usd is not None and est_cost > cfg.cost_budget_usd:
        logger.warning(
            "CognitiveLoop estimated cost $%.4f exceeded budget $%.4f",
            est_cost,
            cfg.cost_budget_usd,
        )

    return final_text, tool_log, thinking_text
