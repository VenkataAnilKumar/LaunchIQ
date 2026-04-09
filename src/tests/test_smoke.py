from __future__ import annotations

import base64
import json
import os

import httpx
import pytest


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _dev_bearer_token(user_id: str = "smoke-user") -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": user_id}).encode()).decode().rstrip("=")
    signature = "x"
    return f"{header}.{payload}.{signature}"


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_dev_bearer_token()}"}


def _request_or_skip(method: str, path: str, **kwargs) -> httpx.Response:
    try:
        return httpx.request(method, f"{API_BASE_URL}{path}", timeout=10, **kwargs)
    except httpx.ConnectError as exc:  # pragma: no cover
        pytest.skip(f"API is not reachable at {API_BASE_URL}: {exc}")


def test_health_ok() -> None:
    response = _request_or_skip("GET", "/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ok"


def test_health_ready() -> None:
    response = _request_or_skip("GET", "/api/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ready"


def test_create_launch_missing_fields_returns_422() -> None:
    response = _request_or_skip(
        "POST",
        "/api/v1/launches",
        json={"product_name": "Only name"},
        headers=_auth_headers(),
    )
    assert response.status_code == 422


def test_get_nonexistent_launch_returns_404() -> None:
    response = _request_or_skip(
        "GET",
        "/api/v1/launches/nonexistent",
        headers=_auth_headers(),
    )
    assert response.status_code == 404
