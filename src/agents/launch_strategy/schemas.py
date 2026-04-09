"""Schema contracts for Launch Strategy outputs."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LaunchPhase(BaseModel):
	phase: Literal["Pre-Launch", "Launch Week", "Post-Launch", "Growth"]
	duration: str
	goals: list[str]
	tactics: list[str] = Field(min_length=3)
	kpis: list[str]


class LaunchStrategyOutput(BaseModel):
	positioning_statement: str
	launch_date_recommendation: str
	phases: list[LaunchPhase] = Field(min_length=3, max_length=4)
	channels: list[str]
	budget_allocation: dict[str, str]
	success_metrics: list[str]
	risks: list[str]

