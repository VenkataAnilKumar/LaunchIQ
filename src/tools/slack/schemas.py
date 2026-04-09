"""Slack tool schemas."""
from __future__ import annotations

from pydantic import BaseModel


class PostMessageInput(BaseModel):
    channel: str
    text: str
    blocks: list[dict] | None = None


class GetChannelInput(BaseModel):
    channel: str
