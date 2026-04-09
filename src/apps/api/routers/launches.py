"""
Launch resource endpoints.

POST /launches          — create a new launch, enqueue orchestrator
GET  /launches/{id}     — get launch + current agent pipeline status
GET  /launches/{id}/stream — SSE stream of agent progress
"""
from __future__ import annotations

import uuid
from typing import Annotated, AsyncIterator

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..services.launch_service import LaunchService, get_launch_service
from ..services.stream_service import StreamService, get_stream_service

router = APIRouter()


# ------------------------------------------------------------------ #
# Request / Response models                                            #
# ------------------------------------------------------------------ #

class LaunchBriefRequest(BaseModel):
    product_name: str
    description: str
    target_market: str
    competitors: list[str] = []
    launch_date: str | None = None


class LaunchResponse(BaseModel):
    launch_id: str
    status: str
    created_at: str


class LaunchDetailResponse(BaseModel):
    launch_id: str
    status: str
    brief: dict
    pipeline: list[dict]   # one entry per agent with status + output
    hitl_pending: bool
    hitl_checkpoint: str | None


# ------------------------------------------------------------------ #
# Routes                                                               #
# ------------------------------------------------------------------ #

@router.post("", response_model=LaunchResponse, status_code=201)
async def create_launch(
    body: LaunchBriefRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[LaunchService, Depends(get_launch_service)],
) -> LaunchResponse:
    launch = await service.create(body.model_dump())
    background_tasks.add_task(service.run_pipeline, launch["launch_id"])
    return LaunchResponse(**launch)


@router.get("/{launch_id}", response_model=LaunchDetailResponse)
async def get_launch(
    launch_id: str,
    service: Annotated[LaunchService, Depends(get_launch_service)],
) -> LaunchDetailResponse:
    launch = await service.get(launch_id)
    if not launch:
        raise HTTPException(status_code=404, detail="Launch not found")
    return LaunchDetailResponse(**launch)


@router.get("/{launch_id}/stream")
async def stream_launch(
    launch_id: str,
    stream_service: Annotated[StreamService, Depends(get_stream_service)],
) -> StreamingResponse:
    """Server-Sent Events stream of agent progress for a launch."""
    return StreamingResponse(
        stream_service.sse_generator(launch_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
