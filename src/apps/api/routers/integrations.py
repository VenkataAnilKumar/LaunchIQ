"""Integrations routes for HubSpot, Slack, and GA4 credentials."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.user_repo import UserRepository

router = APIRouter()


class IntegrationBody(BaseModel):
	credentials: dict[str, Any]


@router.get("")
async def list_integrations(request: Request) -> dict[str, bool]:
	user_id = getattr(request.state, "user_id", None)
	if not user_id:
		raise HTTPException(status_code=401, detail="Unauthorized")

	async with AsyncSessionLocal() as db:
		repo = UserRepository(db)
		user = await repo.get(user_id)
		integrations = (user.integrations if user else {}) or {}
		return {
			"hubspot": "hubspot" in integrations,
			"slack": "slack" in integrations,
			"ga4": "ga4" in integrations,
		}


@router.post("/hubspot")
async def connect_hubspot(request: Request, body: IntegrationBody) -> dict[str, str]:
	return await _connect(request, "hubspot", body.credentials)


@router.delete("/hubspot")
async def disconnect_hubspot(request: Request) -> dict[str, str]:
	return await _disconnect(request, "hubspot")


@router.post("/slack")
async def connect_slack(request: Request, body: IntegrationBody) -> dict[str, str]:
	return await _connect(request, "slack", body.credentials)


@router.delete("/slack")
async def disconnect_slack(request: Request) -> dict[str, str]:
	return await _disconnect(request, "slack")


@router.post("/ga4")
async def connect_ga4(request: Request, body: IntegrationBody) -> dict[str, str]:
	return await _connect(request, "ga4", body.credentials)


@router.delete("/ga4")
async def disconnect_ga4(request: Request) -> dict[str, str]:
	return await _disconnect(request, "ga4")


async def _connect(
	request: Request,
	integration_name: str,
	credentials: dict[str, Any],
) -> dict[str, str]:
	user_id = getattr(request.state, "user_id", None)
	if not user_id:
		raise HTTPException(status_code=401, detail="Unauthorized")

	async with AsyncSessionLocal() as db:
		repo = UserRepository(db)
		await repo.update_integrations(user_id, integration_name, credentials)
	return {"status": "connected"}


async def _disconnect(request: Request, integration_name: str) -> dict[str, str]:
	user_id = getattr(request.state, "user_id", None)
	if not user_id:
		raise HTTPException(status_code=401, detail="Unauthorized")

	async with AsyncSessionLocal() as db:
		repo = UserRepository(db)
		await repo.remove_integration(user_id, integration_name)
	return {"status": "disconnected"}

