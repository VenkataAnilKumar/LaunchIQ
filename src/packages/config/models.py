"""Agent model assignments and pipeline configuration — single source of truth."""
from __future__ import annotations

AGENT_MODELS: dict[str, str] = {
    "orchestrator":        "claude-opus-4-6",
    "market_intelligence": "claude-sonnet-4-6",
    "audience_insight":    "claude-sonnet-4-6",
    "launch_strategy":     "claude-opus-4-6",
    "content_generation":  "claude-sonnet-4-6",
    "analytics_feedback":  "claude-haiku-4-5-20251001",
}

HITL_CHECKPOINTS: list[str] = [
    "brief_review",
    "persona_review",
    "strategy_review",
    "content_review",
]

# Worker agents run in this order inside the orchestrator pipeline.
# The orchestrator itself is excluded from this sequence.
PIPELINE_SEQUENCE: list[str] = [
    "market_intelligence",
    "audience_insight",
    "launch_strategy",
    "content_generation",
]
