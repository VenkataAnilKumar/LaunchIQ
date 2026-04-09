from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import httpx
import pytest


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DEMO_LAUNCH_PATH = Path(__file__).resolve().parents[1] / "data" / "demo" / "demo_launch.json"


def _dev_bearer_token(user_id: str = "integration-user") -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": user_id}).encode()).decode().rstrip("=")
    signature = "x"
    return f"{header}.{payload}.{signature}"


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_dev_bearer_token()}"}


def _load_demo_launch() -> dict[str, object]:
    return json.loads(DEMO_LAUNCH_PATH.read_text(encoding="utf-8"))


@pytest.mark.integration
def test_full_pipeline_e2e() -> None:
    try:
        health = httpx.get(f"{API_BASE_URL}/api/v1/health", timeout=10)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"API is not reachable at {API_BASE_URL}: {exc}")

    if health.status_code != 200:  # pragma: no cover
        pytest.skip(f"API is not healthy at {API_BASE_URL} (status {health.status_code})")

    create_resp = httpx.post(
        f"{API_BASE_URL}/api/v1/launches",
        json=_load_demo_launch(),
        headers=_auth_headers(),
        timeout=30,
    )
    assert create_resp.status_code == 201
    launch_id = create_resp.json()["launch_id"]

    timeout_seconds = 60
    interval_seconds = 2
    deadline = time.time() + timeout_seconds

    first_hitl_seen = False
    second_hitl_seen = False
    completed_seen = False

    while time.time() < deadline:
        detail_resp = httpx.get(
            f"{API_BASE_URL}/api/v1/launches/{launch_id}",
            headers=_auth_headers(),
            timeout=30,
        )
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        status = detail.get("status")

        if status == "hitl_pending" and not first_hitl_seen:
            first_hitl_seen = True
            decide_resp = httpx.post(
                f"{API_BASE_URL}/api/v1/hitl/{launch_id}/decide",
                json={"decision": "approve"},
                headers=_auth_headers(),
                timeout=30,
            )
            assert decide_resp.status_code == 200

        elif status == "hitl_pending" and first_hitl_seen and not second_hitl_seen:
            second_hitl_seen = True
            decide_resp = httpx.post(
                f"{API_BASE_URL}/api/v1/hitl/{launch_id}/decide",
                json={"decision": "approve"},
                headers=_auth_headers(),
                timeout=30,
            )
            assert decide_resp.status_code == 200

        elif status == "completed":
            completed_seen = True
            break

        time.sleep(interval_seconds)

    assert first_hitl_seen, "Expected first HITL checkpoint was not reached"
    assert second_hitl_seen, "Expected second HITL checkpoint was not reached"
    assert completed_seen, "Launch pipeline did not reach completed within timeout"

    final_resp = httpx.get(
        f"{API_BASE_URL}/api/v1/launches/{launch_id}",
        headers=_auth_headers(),
        timeout=30,
    )
    assert final_resp.status_code == 200
    final_data = final_resp.json()

    pipeline = final_data.get("pipeline", [])
    assert pipeline
    assert all(item.get("status") == "completed" for item in pipeline)

    brief = final_data.get("brief", {})
    assert isinstance(brief, dict)
    for key in ("market_intelligence", "audience_insight", "launch_strategy", "content_generation"):
        assert key in brief
