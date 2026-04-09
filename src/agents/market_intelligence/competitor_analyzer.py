"""Competitor analysis helper."""
from __future__ import annotations

from typing import Any


class CompetitorAnalyzer:
	def analyze(
		self,
		search_results: list[dict[str, Any]],
		known_competitors: list[str],
	) -> list[dict[str, Any]]:
		base = [
			{
				"name": name,
				"positioning": "Established player in adjacent category.",
				"strengths": ["Existing customer base", "Mature feature set"],
				"weaknesses": ["Generalized workflows", "Less specialized UX"],
				"pricing": None,
			}
			for name in known_competitors
		]

		for item in search_results:
			title = str(item.get("title", "")).strip()
			if not title:
				continue
			candidate = title.split("|")[0].strip()
			if not any(c["name"].lower() == candidate.lower() for c in base):
				base.append(
					{
						"name": candidate,
						"positioning": str(item.get("content", ""))[:160] or "N/A",
						"strengths": ["Clear message"],
						"weaknesses": ["Unknown differentiation"],
						"pricing": None,
					}
				)
			if len(base) >= 10:
				break

		return base[:10]

