from __future__ import annotations

import base64
import json
from collections.abc import AsyncIterator
from pathlib import Path
import types
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

fake_db_module = types.ModuleType("src.memory.structured.database")
fake_db_module.AsyncSessionLocal = lambda: None
sys.modules.setdefault("src.memory.structured.database", fake_db_module)

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import src.apps.api.routers.integrations as integrations_router
from src.apps.api.middleware.auth import ClerkAuthMiddleware


app = FastAPI()
app.add_middleware(ClerkAuthMiddleware)
app.include_router(
    integrations_router.router,
    prefix="/api/v1/integrations",
    tags=["integrations"],
)


def _b64(data: dict[str, str]) -> str:
    raw = json.dumps(data).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def build_dev_token(user_id: str) -> str:
    return f"{_b64({'alg': 'none', 'typ': 'JWT'})}.{_b64({'sub': user_id})}.dev"


class FakeSessionContext:
    async def __aenter__(self) -> object:
        return object()

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False


class FakeRepo:
    store: dict[str, dict[str, dict[str, object]]] = {}

    def __init__(self, _db: object) -> None:
        pass

    def _default(self, name: str) -> dict[str, object]:
        return {
            "name": name,
            "status": "disconnected",
            "connected": False,
            "has_credentials": False,
            "connected_at": None,
            "updated_at": None,
            "disconnected_at": None,
            "last_error": None,
            "configured_fields": [],
        }

    async def list_integration_metadata(self, user_id: str) -> dict[str, dict[str, object]]:
        current = self.store.get(user_id, {})
        return {
            "hubspot": dict(current.get("hubspot", self._default("hubspot"))),
            "slack": dict(current.get("slack", self._default("slack"))),
            "ga4": dict(current.get("ga4", self._default("ga4"))),
        }

    async def update_integrations(self, user_id: str, integration_name: str, credentials: dict[str, object]) -> None:
        bucket = self.store.setdefault(user_id, {})
        bucket[integration_name] = {
            "name": integration_name,
            "status": "connected",
            "connected": True,
            "has_credentials": True,
            "connected_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
            "disconnected_at": None,
            "last_error": None,
            "configured_fields": sorted(credentials.keys()),
        }

    async def remove_integration(self, user_id: str, integration_name: str) -> None:
        bucket = self.store.setdefault(user_id, {})
        current = dict(bucket.get(integration_name, self._default(integration_name)))
        current.update(
            {
                "status": "disconnected",
                "connected": False,
                "has_credentials": False,
                "disconnected_at": "2026-01-02T00:00:00+00:00",
                "updated_at": "2026-01-02T00:00:00+00:00",
            }
        )
        bucket[integration_name] = current

    async def set_integration_error(self, user_id: str, integration_name: str, error_message: str | None) -> None:
        bucket = self.store.setdefault(user_id, {})
        current = dict(bucket.get(integration_name, self._default(integration_name)))
        current["last_error"] = error_message
        current["updated_at"] = "2026-01-03T00:00:00+00:00"
        bucket[integration_name] = current


@pytest.fixture(autouse=True)
def reset_repo_state() -> None:
    FakeRepo.store.clear()


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[TestClient]:
    async def fake_validate(_name: str, _credentials: dict[str, object]) -> tuple[bool, str]:
        return True, "ok"

    monkeypatch.setattr(integrations_router, "AsyncSessionLocal", lambda: FakeSessionContext())
    monkeypatch.setattr(integrations_router, "UserRepository", FakeRepo)
    monkeypatch.setattr(integrations_router, "validate_integration_credentials", fake_validate)

    with TestClient(app) as client:
        yield client


def auth_headers(user_id: str = "user_1") -> dict[str, str]:
    return {"Authorization": f"Bearer {build_dev_token(user_id)}"}


def test_list_integrations_defaults(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/integrations", headers=auth_headers())
    assert response.status_code == 200

    payload = response.json()
    assert payload["connected_count"] == 0
    assert payload["integrations"]["hubspot"]["connected"] is False
    assert payload["integrations"]["slack"]["status"] == "disconnected"


def test_connect_and_disconnect_metadata(api_client: TestClient) -> None:
    connect = api_client.post(
        "/api/v1/integrations/slack",
        headers=auth_headers(),
        json={"credentials": {"bot_token": "xoxb-test", "channel_id": "C123"}},
    )
    assert connect.status_code == 200
    body = connect.json()
    assert body["status"] == "connected"
    assert body["metadata"]["connected"] is True
    assert "bot_token" in body["metadata"]["configured_fields"]

    disconnect = api_client.delete("/api/v1/integrations/slack", headers=auth_headers())
    assert disconnect.status_code == 200
    payload = disconnect.json()
    assert payload["status"] == "disconnected"
    assert payload["metadata"]["connected"] is False


def test_test_endpoint_and_validation_failure(api_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    async def failing_validate(name: str, _credentials: dict[str, object]) -> tuple[bool, str]:
        return False, f"{name} invalid"

    tested = api_client.post(
        "/api/v1/integrations/test/hubspot",
        headers=auth_headers(),
        json={"credentials": {"access_token": "abc"}},
    )
    assert tested.status_code == 200
    assert tested.json()["valid"] is True

    monkeypatch.setattr(integrations_router, "validate_integration_credentials", failing_validate)

    failed_connect = api_client.post(
        "/api/v1/integrations/hubspot",
        headers=auth_headers(),
        json={"credentials": {"access_token": "bad"}},
    )
    assert failed_connect.status_code == 400

    listed = api_client.get("/api/v1/integrations", headers=auth_headers())
    assert listed.status_code == 200
    assert listed.json()["integrations"]["hubspot"]["last_error"] == "hubspot invalid"
