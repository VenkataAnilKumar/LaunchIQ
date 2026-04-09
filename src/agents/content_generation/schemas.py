"""Schema contracts for Content Generation outputs."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ContentItem(BaseModel):
	format: Literal["email", "linkedin", "twitter", "ad_copy", "landing_page"]
	variant: Literal["a", "b"]
	headline: str
	body: str
	cta: str
	target_persona: str


class ContentBundle(BaseModel):
	email_sequence: list[ContentItem] = Field(min_length=3, max_length=5)
	social_posts: list[ContentItem] = Field(min_length=3, max_length=10)
	ad_copy: list[ContentItem] = Field(min_length=2, max_length=4)
	brand_voice_notes: str

