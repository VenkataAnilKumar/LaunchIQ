"""Anomaly detection helper."""
from __future__ import annotations


class AnomalyDetector:
	def detect(self, metrics: dict) -> list[str]:
		anomalies: list[str] = []
		engagement = float(metrics.get("engagement_rate", 0) or 0)
		conversion = float(metrics.get("conversion_rate", 0) or 0)

		if engagement < 0.3:
			anomalies.append("engagement_rate_low")
		if conversion < 0.02:
			anomalies.append("conversion_rate_low")
		if float(metrics.get("sessions", 0) or 0) < 100:
			anomalies.append("traffic_volume_low")
		return anomalies

