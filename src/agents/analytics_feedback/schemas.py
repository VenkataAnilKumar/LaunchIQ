"""Schema contracts for Analytics & Feedback outputs."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
	area: str
	insight: str
	action: str
	priority: Literal["high", "medium", "low"]


class AnalyticsOutput(BaseModel):
	engagement_score: float = Field(ge=0.0, le=1.0)
	top_performing_content: list[str]
	underperforming_content: list[str]
	recommendations: list[Recommendation] = Field(min_length=3)
	predicted_next_action: str

