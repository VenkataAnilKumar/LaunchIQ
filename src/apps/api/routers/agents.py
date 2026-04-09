"""
Agent status and retry endpoints.

GET  /agents/{launch_id}           — pipeline status for all agents
POST /agents/{launch_id}/{agent}/retry — re-run a single agent
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..services.agent_service import AgentService, get_agent_service

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
    service: Annotated[AgentService, Depends(get_agent_service)],
) -> AgentStatusResponse:
    statuses = await service.get_pipeline_status(launch_id)
    if statuses is None:
        raise HTTPException(status_code=404, detail="Launch not found")
    return AgentStatusResponse(launch_id=launch_id, agents=statuses)


@router.post("/{launch_id}/{agent_id}/retry", response_model=RetryResponse)
async def retry_agent(
    launch_id: str,
    agent_id: str,
    service: Annotated[AgentService, Depends(get_agent_service)],
) -> RetryResponse:
    result = await service.retry(launch_id, agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Launch or agent not found")
    return RetryResponse(launch_id=launch_id, agent_id=agent_id, status="queued")
