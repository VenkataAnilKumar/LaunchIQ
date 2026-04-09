"""Market research helper logic for search-query construction and extraction."""
from __future__ import annotations

from typing import Any


class MarketResearcher:
	def build_search_queries(self, brief: dict[str, Any]) -> list[str]:
		product = str(brief.get("product_name", "Product"))
		market = str(brief.get("target_market", "target market"))
		competitors = brief.get("competitors", []) or []

		queries = [
			f"{product} market size 2026",
			f"{market} trends 2026",
			f"{product} positioning examples",
			f"{product} customer pain points",
		]
		for name in competitors[:2]:
			queries.append(f"{name} pricing positioning")

		return queries[:6]

	def extract_competitor_data(self, search_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
		competitors: list[dict[str, Any]] = []
		for item in search_results:
			title = str(item.get("title", "")).strip()
			if not title:
				continue
			competitors.append(
				{
					"name": title.split("|")[0].strip(),
					"positioning": str(item.get("content", ""))[:180] or "N/A",
					"strengths": ["Brand recognition", "Feature breadth"],
					"weaknesses": ["Complex setup", "Higher cost"],
					"pricing": None,
				}
			)
			if len(competitors) >= 10:
				break
		return competitors

