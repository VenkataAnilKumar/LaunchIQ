"""GA4 tool schemas."""
from __future__ import annotations

from pydantic import BaseModel


class GetMetricsInput(BaseModel):
    property_id: str
    metrics: list[str]
    dimensions: list[str] | None = None
    date_range: dict | None = None


class MetricsResponse(BaseModel):
    property_id: str
    metrics: dict[str, float]
