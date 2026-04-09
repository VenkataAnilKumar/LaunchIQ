"""Metrics aggregation helper."""
from __future__ import annotations

from typing import Any


class MetricsAggregator:
	def aggregate(self, ga4_data: dict[str, Any]) -> dict[str, float]:
		metrics = ga4_data.get("metrics", {}) if isinstance(ga4_data, dict) else {}
		sessions = float(metrics.get("sessions", 0) or 0)
		conversions = float(metrics.get("conversions", 0) or 0)
		engagement = float(metrics.get("engagement_rate", 0) or 0)
		conversion_rate = (conversions / sessions) if sessions > 0 else 0.0
		return {
			"sessions": sessions,
			"conversions": conversions,
			"engagement_rate": engagement,
			"conversion_rate": conversion_rate,
		}

