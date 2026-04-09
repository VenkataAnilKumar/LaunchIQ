"""Schema contracts for Market Intelligence agent outputs."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Competitor(BaseModel):
	name: str
	positioning: str
	strengths: list[str]
	weaknesses: list[str]
	pricing: str | None = None


class MarketTrend(BaseModel):
	trend: str
	relevance: str
	source: str | None = None


class MarketIntelligenceOutput(BaseModel):
	market_size: str
	growth_rate: str
	competitors: list[Competitor] = Field(min_length=1, max_length=10)
	trends: list[MarketTrend] = Field(min_length=1, max_length=10)
	white_space: str
	recommended_positioning: str

