"""Slack SDK auth helper."""
from __future__ import annotations

from typing import Any


def get_slack_client(bot_token: str) -> Any:
    if not bot_token:
        raise ValueError("Missing Slack bot token")
    try:
        from slack_sdk import WebClient
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("slack-sdk is not installed") from exc
    return WebClient(token=bot_token)
