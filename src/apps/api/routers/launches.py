"""
Launch resource endpoints.

POST /launches          — create a new launch, enqueue orchestrator
GET  /launches/{id}     — get launch + current agent pipeline status
GET  /launches/{id}/stream — SSE stream of agent progress
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field

from src.agents._base.llm import AgentError

from ..services.launch_service import LaunchService, StateError, get_launch_service
from ..services.stream_service import StreamService, get_stream_service

router = APIRouter()


# ------------------------------------------------------------------ #
# Request / Response models                                            #
# ------------------------------------------------------------------ #

def current_user(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_id


class LaunchBriefRequest(BaseModel):
    product_name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=10, max_length=5000)
    target_market: str = Field(min_length=1, max_length=255)
    competitors: list[str] = Field(default_factory=list, max_length=10)
    launch_date: str | None = Field(default=None, max_length=50)


class LaunchResponse(BaseModel):
    launch_id: str
    status: str
    created_at: str


class LaunchListItem(BaseModel):
    launch_id: str
    status: str
    product_name: str
    description: str
    target_market: str
    competitors: list[str]
    launch_date: str | None = None
    created_at: str
    updated_at: str


class LaunchDetailResponse(BaseModel):
    launch_id: str
    status: str
    input: dict = {}
    brief: dict            # market_data / personas / strategy / content, as each agent finishes
    pipeline: list[dict]   # one entry per agent with status + output
    hitl_pending: bool
    hitl_checkpoint: str | None
    total_cost_usd: float = 0.0
    export_ready: bool = False


# ------------------------------------------------------------------ #
# Routes                                                               #
# ------------------------------------------------------------------ #

@router.post("", response_model=LaunchResponse, status_code=201)
async def create_launch(
    request: Request,
    body: LaunchBriefRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[LaunchService, Depends(get_launch_service)],
) -> LaunchResponse:
    launch = await service.create(body.model_dump(), user_id=current_user(request))
    background_tasks.add_task(service.run_pipeline, launch["launch_id"])
    return LaunchResponse(**launch)


@router.get("", response_model=list[LaunchListItem])
async def list_launches(
    request: Request,
    service: Annotated[LaunchService, Depends(get_launch_service)],
) -> list[LaunchListItem]:
    launches = await service.list_by_user(current_user(request))
    return [LaunchListItem(**launch) for launch in launches]


@router.get("/{launch_id}", response_model=LaunchDetailResponse)
async def get_launch(
    launch_id: str,
    request: Request,
    service: Annotated[LaunchService, Depends(get_launch_service)],
) -> LaunchDetailResponse:
    launch = await service.get(launch_id, user_id=current_user(request))
    if not launch:
        raise HTTPException(status_code=404, detail="Launch not found")
    return LaunchDetailResponse(**launch)


class AnalyticsRequest(BaseModel):
    # Measured results only (sessions, conversions, engagement_rate, per-content CTR, ...).
    metrics: dict = Field(min_length=1)


@router.post("/{launch_id}/analytics")
async def analyze_launch(
    launch_id: str,
    body: AnalyticsRequest,
    request: Request,
    service: Annotated[LaunchService, Depends(get_launch_service)],
) -> dict:
    """Post-launch feedback: recommendations grounded in the metrics you supply."""
    try:
        return await service.analyze(launch_id, current_user(request), body.metrics)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Launch not found") from exc
    except StateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except AgentError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{launch_id}/export")
async def export_launch(
    launch_id: str,
    request: Request,
    service: Annotated[LaunchService, Depends(get_launch_service)],
    format: str = "md",
):
    """Download the finished launch brief as Markdown (md) or JSON."""
    brief = await service.get_export(launch_id, user_id=current_user(request))
    if brief is None:
        raise HTTPException(status_code=404, detail="Launch not found or not finished yet")
    if format == "json":
        return brief
    if format != "md":
        raise HTTPException(status_code=422, detail="format must be md or json")
    safe = "".join(c if c.isalnum() else "-" for c in str(brief.get("product_name", "launch"))).strip("-").lower()
    return PlainTextResponse(
        brief["markdown"],
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{safe or "launch"}-brief.md"'},
    )


@router.get("/{launch_id}/stream")
async def stream_launch(
    launch_id: str,
    request: Request,
    service: Annotated[LaunchService, Depends(get_launch_service)],
    stream_service: Annotated[StreamService, Depends(get_stream_service)],
) -> StreamingResponse:
    """Server-Sent Events stream of agent progress for a launch."""
    if not await service.owns(launch_id, current_user(request)):
        raise HTTPException(status_code=404, detail="Launch not found")
    return StreamingResponse(
        stream_service.sse_generator(launch_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
