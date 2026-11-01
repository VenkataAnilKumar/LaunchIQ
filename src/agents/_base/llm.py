"""LLM client factory, model resolution, pricing and shared JSON helpers.

Every agent talks to the model through ``get_client()``. The returned object
exposes an *async* ``messages.create(**params)`` compatible with the Anthropic
SDK, so the real ``AsyncAnthropic`` client and the offline ``FakeAnthropic``
client are interchangeable (``LLM_PROVIDER=fake``).
"""
from __future__ import annotations

import json
import re
from typing import Any

from src.apps.api.config import get_settings


class AgentError(RuntimeError):
    """Raised when an agent cannot produce a valid result (API, parsing, budget)."""


class BudgetExceededError(AgentError):
    """Raised when a launch exceeds its configured cost budget."""


# USD per million tokens (input, output) keyed by model family substring.
_PRICING: tuple[tuple[str, tuple[float, float]], ...] = (
    ("opus", (15.0, 75.0)),
    ("haiku", (1.0, 5.0)),
    ("sonnet", (3.0, 15.0)),
)
_DEFAULT_PRICING = (3.0, 15.0)


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Rough cost estimate using per-family list prices. Never raises."""
    in_rate, out_rate = _DEFAULT_PRICING
    lowered = (model or "").lower()
    for key, rates in _PRICING:
        if key in lowered:
            in_rate, out_rate = rates
            break
    return round(
        (input_tokens / 1_000_000) * in_rate + (output_tokens / 1_000_000) * out_rate, 6
    )


def resolve_model(model: str) -> str:
    """Map a tier alias (``opus``/``sonnet``/``haiku``) or a literal id to a model id."""
    settings = get_settings()
    aliases = {
        "opus": settings.anthropic_model_opus,
        "sonnet": settings.anthropic_model_sonnet,
        "haiku": settings.anthropic_model_haiku,
    }
    return aliases.get(model, model)


_client: Any | None = None


def get_client() -> Any:
    """Return a process-wide async LLM client (lazy; no key needed to import)."""
    global _client
    settings = get_settings()
    if settings.llm_provider == "fake":
        from .fake_llm import FakeAnthropic

        if not isinstance(_client, FakeAnthropic):
            _client = FakeAnthropic()
        return _client

    if not settings.anthropic_api_key:
        raise AgentError(
            "ANTHROPIC_API_KEY is not set. Set it, or use LLM_PROVIDER=fake for offline runs."
        )
    import anthropic

    if not isinstance(_client, anthropic.AsyncAnthropic):
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


def reset_client() -> None:
    """Drop the cached client (tests / settings changes)."""
    global _client
    _client = None


def extract_json(text: str) -> dict[str, Any]:
    """Parse the first JSON object from model text (fenced or bare)."""
    if not text or not text.strip():
        raise AgentError("Model returned an empty response")
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    raw = fenced.group(1) if fenced else text.strip()
    if not raw.startswith("{"):
        match = re.search(r"(\{.*\})", raw, re.DOTALL)
        if match:
            raw = match.group(1)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentError(f"Model output was not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise AgentError("Model output JSON was not an object")
    return parsed
