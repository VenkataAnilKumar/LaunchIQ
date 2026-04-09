"""Phase planning helper."""
from __future__ import annotations

from typing import Any


class PhaseBuilder:
	def build_phases(self, market_data: dict[str, Any], personas: dict[str, Any]) -> list[dict[str, Any]]:
		_ = market_data
		_ = personas
		return [
			{
				"phase": "Pre-Launch",
				"duration": "Weeks 1-3",
				"goals": ["Validate positioning", "Build waitlist demand"],
				"tactics": ["Landing page A/B test", "Founder-led social proof", "Partner outreach"],
				"kpis": ["Waitlist signups", "CTR", "Demo requests"],
			},
			{
				"phase": "Launch Week",
				"duration": "Week 4",
				"goals": ["Drive conversion", "Collect user feedback"],
				"tactics": ["Product Hunt launch", "Email sequence", "Live demo webinar"],
				"kpis": ["Signups", "Activation rate", "CAC"],
			},
			{
				"phase": "Post-Launch",
				"duration": "Weeks 5-8",
				"goals": ["Improve retention", "Refine messaging"],
				"tactics": ["Onboarding optimization", "Persona-specific nurture", "Case-study content"],
				"kpis": ["Week-4 retention", "Trial-to-paid", "NPS"],
			},
		]

