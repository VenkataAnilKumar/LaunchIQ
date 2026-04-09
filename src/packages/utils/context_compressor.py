"""Context window compression utilities.

Used by agents to trim their message history before hitting the
context limit without discarding the most recent user message.
"""
from __future__ import annotations

from .token_counter import estimate_messages_tokens, estimate_tokens


def truncate_to_budget(text: str, max_tokens: int) -> str:
    """Truncate *text* so it fits within *max_tokens* (4 chars/token heuristic)."""
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def compress_messages(messages: list[dict], max_tokens: int) -> list[dict]:
    """Drop oldest messages until the list fits within *max_tokens*.

    The last user message is always preserved.
    """
    if not messages or estimate_messages_tokens(messages) <= max_tokens:
        return messages

    # Find the index of the last user message.
    last_user_idx: int | None = None
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "user":
            last_user_idx = i
            break

    if last_user_idx is None:
        # No user message — drop from the front until we fit.
        result = list(messages)
        while result and estimate_messages_tokens(result) > max_tokens:
            result.pop(0)
        return result

    prefix = list(messages[:last_user_idx])
    tail = list(messages[last_user_idx:])

    while prefix and estimate_messages_tokens(prefix + tail) > max_tokens:
        prefix.pop(0)

    return prefix + tail
