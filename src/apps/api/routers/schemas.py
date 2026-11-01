"""JSON Schemas of agent outputs, so the UI can build review/edit forms from the same contract
the API validates edits against."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..services.hitl_service import AGENT_OUTPUT_SCHEMAS

router = APIRouter()


@router.get("/{agent_id}")
async def get_agent_schema(agent_id: str) -> dict:
    schema = AGENT_OUTPUT_SCHEMAS.get(agent_id)
    if schema is None:
        raise HTTPException(status_code=404, detail="Unknown agent")
    return schema.model_json_schema()
