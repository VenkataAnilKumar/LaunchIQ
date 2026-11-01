"""
HITL (Human-in-the-Loop) endpoints.

HITL is a structural pipeline pause — not a UX layer.
When an agent sets hitl_required=True, the pipeline blocks and waits
for an explicit human decision before the next agent runs.

POST /hitl/{launch_id}/approve  — approve and continue pipeline
POST /hitl/{launch_id}/edit     — submit edits and continue
POST /hitl/{launch_id}/reject   — reject and halt pipeline
GET  /hitl/{launch_id}/pending  — get the current pending checkpoint
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ..services.hitl_service import (
    CheckpointMismatchError,
    HITLService,
    InvalidEditsError,
    get_hitl_service,
)
from ..services.launch_service import LaunchService, get_launch_service
from .launches import current_user

router = APIRouter()


class HITLDecision(BaseModel):
    decision: str  # "approve" | "edit" | "reject"
    edits: dict | None = None
    comment: str | None = None
    checkpoint: str | None = None  # the checkpoint this decision was made for (stale-click guard)


class HITLPendingResponse(BaseModel):
    launch_id: str
    checkpoint: str
    agent_id: str
    output_preview: dict
    created_at: str


async def _require_owner(launch_id: str, request: Request, launches: LaunchService) -> None:
    if not await launches.owns(launch_id, current_user(request)):
        raise HTTPException(status_code=404, detail="Launch not found")


@router.get("/{launch_id}/pending", response_model=HITLPendingResponse | None)
async def get_pending(
    launch_id: str,
    request: Request,
    service: Annotated[HITLService, Depends(get_hitl_service)],
    launches: Annotated[LaunchService, Depends(get_launch_service)],
) -> HITLPendingResponse | None:
    await _require_owner(launch_id, request, launches)
    pending = await service.get_pending(launch_id)
    if not pending:
        return None
    return HITLPendingResponse(**pending)


@router.post("/{launch_id}/decide")
async def decide(
    launch_id: str,
    body: HITLDecision,
    request: Request,
    service: Annotated[HITLService, Depends(get_hitl_service)],
    launches: Annotated[LaunchService, Depends(get_launch_service)],
) -> dict:
    await _require_owner(launch_id, request, launches)
    if body.decision not in ("approve", "edit", "reject"):
        raise HTTPException(status_code=422, detail="decision must be approve | edit | reject")

    try:
        result = await service.resolve(launch_id, body.decision, body.edits, body.comment, body.checkpoint)
    except CheckpointMismatchError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidEditsError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not result:
        raise HTTPException(status_code=404, detail="No pending HITL checkpoint for this launch")
    return {"status": "resolved", "next_step": result.get("next_step")}
