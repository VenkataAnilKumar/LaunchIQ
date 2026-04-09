"""Trend extraction helper."""
from __future__ import annotations

from typing import Any


class TrendDetector:
	def extract_trends(self, search_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
		trends: list[dict[str, Any]] = []
		for item in search_results:
			content = str(item.get("content", "")).strip()
			title = str(item.get("title", "")).strip() or "Unknown source"
			if not content:
				continue
			trends.append(
				{
					"trend": content[:80],
					"relevance": "Impacts go-to-market execution and messaging.",
					"source": title,
				}
			)
			if len(trends) >= 10:
				break
		return trends

