"""
Agent status and retry endpoints.

GET  /agents/{launch_id}           — pipeline status for all agents
POST /agents/{launch_id}/{agent}/retry — re-run a single agent
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ..services.agent_service import AgentService, get_agent_service
from ..services.launch_service import LaunchService, get_launch_service
from .launches import current_user

router = APIRouter()


class AgentStatusResponse(BaseModel):
    launch_id: str
    agents: list[dict]   # [{agent_id, status, started_at, completed_at, output}]


class RetryResponse(BaseModel):
    launch_id: str
    agent_id: str
    status: str


@router.get("/{launch_id}", response_model=AgentStatusResponse)
async def get_agent_status(
    launch_id: str,
    request: Request,
    service: Annotated[AgentService, Depends(get_agent_service)],
    launches: Annotated[LaunchService, Depends(get_launch_service)],
) -> AgentStatusResponse:
    if not await launches.owns(launch_id, current_user(request)):
        raise HTTPException(status_code=404, detail="Launch not found")
    statuses = await service.get_pipeline_status(launch_id)
    if statuses is None:
        raise HTTPException(status_code=404, detail="Launch not found")
    return AgentStatusResponse(launch_id=launch_id, agents=statuses)


@router.post("/{launch_id}/{agent_id}/retry", response_model=RetryResponse)
async def retry_agent(
    launch_id: str,
    agent_id: str,
    request: Request,
    service: Annotated[AgentService, Depends(get_agent_service)],
    launches: Annotated[LaunchService, Depends(get_launch_service)],
) -> RetryResponse:
    """Re-run an agent that failed; the pipeline resumes from that agent."""
    if not await launches.owns(launch_id, current_user(request)):
        raise HTTPException(status_code=404, detail="Launch not found")
    outcome = await service.retry(launch_id, agent_id)
    if outcome == "not_found":
        raise HTTPException(status_code=404, detail="Agent not found for this launch")
    if outcome == "not_failed":
        raise HTTPException(status_code=409, detail="Only failed agents can be retried")
    return RetryResponse(launch_id=launch_id, agent_id=agent_id, status="queued")
