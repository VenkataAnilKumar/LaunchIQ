"""Schema contracts for Audience Insight outputs."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Persona(BaseModel):
	name: str
	role: str
	age_range: str
	pain_points: list[str] = Field(min_length=2, max_length=5)
	goals: list[str] = Field(min_length=2, max_length=5)
	channels: list[str]
	message_hook: str = Field(max_length=120)
	willingness_to_pay: str


class AudienceInsightOutput(BaseModel):
	primary_persona: Persona
	secondary_personas: list[Persona] = Field(default_factory=list, max_length=3)
	icp_summary: str
	messaging_framework: dict[str, str]
	recommended_channels: list[str]

