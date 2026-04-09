"""GA4 SDK auth helper."""
from __future__ import annotations

from typing import Any


def get_ga4_client(credentials: dict[str, Any]) -> Any:
    if not credentials:
        raise ValueError("Missing GA4 credentials")
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("google-analytics-data SDK is not installed") from exc

    # Placeholder client; real credential handling is wired in deployment env.
    return BetaAnalyticsDataClient()
