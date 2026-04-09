"""Pydantic schemas for Tavily search integration."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TavilySearchInput(BaseModel):
	query: str = Field(min_length=3)
	max_results: int = Field(default=5, ge=1, le=10)
	search_depth: str = "advanced"


class TavilySearchResult(BaseModel):
	results: list[dict]
	answer: str | None = None
	query: str

