"""Lightweight token estimator (no external dependencies).

Uses the 4-chars ≈ 1-token heuristic for budget checks. Accurate enough
for guard-railing context windows — not for billing.
"""
from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """Estimate token count: 4 characters ≈ 1 token."""
    return max(1, len(text) // 4)


def estimate_messages_tokens(messages: list[dict]) -> int:
    """Sum estimated tokens across a messages list.

    Handles both string content and list-of-blocks content (Anthropic format).
    """
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += estimate_tokens(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    total += estimate_tokens(block.get("text", ""))
    return total


def is_within_budget(messages: list[dict], budget: int = 180_000) -> bool:
    """Return True if the messages list fits within the token budget."""
    return estimate_messages_tokens(messages) <= budget
