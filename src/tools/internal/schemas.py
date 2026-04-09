"""Schemas for internal MCP tools."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class GetPriorOutputInput(BaseModel):
    launch_id: str
    agent_id: str


class SaveOutputInput(BaseModel):
    launch_id: str
    agent_id: str
    output: dict[str, Any]


class GetBriefInput(BaseModel):
    launch_id: str


class SessionDataInput(BaseModel):
    launch_id: str
    key: str


class SetSessionDataInput(SessionDataInput):
    value: dict[str, Any]
