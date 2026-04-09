"""Integrations routes for HubSpot, Slack, and GA4 credentials."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.apps.api.services.integration_validation import (
	IntegrationValidationError,
	validate_integration_credentials,
)
from src.memory.structured.database import AsyncSessionLocal
from src.memory.structured.repositories.user_repo import UserRepository

router = APIRouter()


class IntegrationBody(BaseModel):
	credentials: dict[str, Any]


class IntegrationMetadata(BaseModel):
	name: str
	status: str
	connected: bool
	has_credentials: bool
	connected_at: str | None = None
	updated_at: str | None = None
	disconnected_at: str | None = None
	last_error: str | None = None
	configured_fields: list[str] = []


class IntegrationListResponse(BaseModel):
	integrations: dict[str, IntegrationMetadata]
	connected_count: int
	updated_at: str | None = None


class IntegrationMutationResponse(BaseModel):
	integration: str
	status: str
	metadata: IntegrationMetadata


class IntegrationTestResponse(BaseModel):
	integration: str
	valid: bool
	message: str


@router.get("")
async def list_integrations(request: Request) -> IntegrationListResponse:
	user_id = getattr(request.state, "user_id", None)
	if not user_id:
		raise HTTPException(status_code=401, detail="Unauthorized")

	async with AsyncSessionLocal() as db:
		repo = UserRepository(db)
		metadata = await repo.list_integration_metadata(user_id)
		connected_count = sum(1 for item in metadata.values() if item.get("connected"))
		latest = max(
			(
				item.get("updated_at")
				for item in metadata.values()
				if isinstance(item.get("updated_at"), str)
			),
			default=None,
		)
		return IntegrationListResponse(
			integrations={name: IntegrationMetadata(**item) for name, item in metadata.items()},
			connected_count=connected_count,
			updated_at=latest,
		)


@router.post("/hubspot")
async def connect_hubspot(request: Request, body: IntegrationBody) -> IntegrationMutationResponse:
	return await _connect(request, "hubspot", body.credentials)


@router.delete("/hubspot")
async def disconnect_hubspot(request: Request) -> IntegrationMutationResponse:
	return await _disconnect(request, "hubspot")


@router.post("/slack")
async def connect_slack(request: Request, body: IntegrationBody) -> IntegrationMutationResponse:
	return await _connect(request, "slack", body.credentials)


@router.delete("/slack")
async def disconnect_slack(request: Request) -> IntegrationMutationResponse:
	return await _disconnect(request, "slack")


@router.post("/ga4")
async def connect_ga4(request: Request, body: IntegrationBody) -> IntegrationMutationResponse:
	return await _connect(request, "ga4", body.credentials)


@router.delete("/ga4")
async def disconnect_ga4(request: Request) -> IntegrationMutationResponse:
	return await _disconnect(request, "ga4")


@router.post("/test/{integration_name}")
async def test_integration(
	request: Request,
	integration_name: str,
	body: IntegrationBody,
) -> IntegrationTestResponse:
	user_id = getattr(request.state, "user_id", None)
	if not user_id:
		raise HTTPException(status_code=401, detail="Unauthorized")

	if integration_name not in {"hubspot", "slack", "ga4"}:
		raise HTTPException(status_code=404, detail="Unsupported integration")

	try:
		valid, message = await validate_integration_credentials(integration_name, body.credentials)
	except IntegrationValidationError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc

	return IntegrationTestResponse(
		integration=integration_name,
		valid=valid,
		message=message,
	)


async def _connect(
	request: Request,
	integration_name: str,
	credentials: dict[str, Any],
) -> IntegrationMutationResponse:
	user_id = getattr(request.state, "user_id", None)
	if not user_id:
		raise HTTPException(status_code=401, detail="Unauthorized")

	async with AsyncSessionLocal() as db:
		repo = UserRepository(db)

		valid, message = await validate_integration_credentials(integration_name, credentials)
		if not valid:
			await repo.set_integration_error(user_id, integration_name, message)
			raise HTTPException(status_code=400, detail=message)

		await repo.update_integrations(user_id, integration_name, credentials)
		await repo.set_integration_error(user_id, integration_name, None)
		metadata = await repo.list_integration_metadata(user_id)
		entry = metadata[integration_name]
		return IntegrationMutationResponse(
			integration=integration_name,
			status="connected",
			metadata=IntegrationMetadata(**entry),
		)


async def _disconnect(request: Request, integration_name: str) -> IntegrationMutationResponse:
	user_id = getattr(request.state, "user_id", None)
	if not user_id:
		raise HTTPException(status_code=401, detail="Unauthorized")

	async with AsyncSessionLocal() as db:
		repo = UserRepository(db)
		await repo.remove_integration(user_id, integration_name)
		await repo.set_integration_error(user_id, integration_name, None)
		metadata = await repo.list_integration_metadata(user_id)
		entry = metadata[integration_name]
		return IntegrationMutationResponse(
			integration=integration_name,
			status="disconnected",
			metadata=IntegrationMetadata(**entry),
		)

