"""Health check endpoints — used by load balancers and smoke tests."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/api/v1/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")


@router.get("/api/v1/health/ready")
async def readiness() -> dict[str, str]:
    """Readiness probe — extend to check DB/Redis connectivity."""
    return {"status": "ready"}
