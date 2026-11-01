"""End-to-end API tests: real FastAPI app + real SQLite + fake LLM, no external services."""
from __future__ import annotations

import base64
import json

import httpx
import pytest
import pytest_asyncio

from src.agents.orchestrator.dispatcher import AgentDispatcher
from src.apps.api.main import app
from src.apps.api.workers.runner import drain_background
from src.memory.structured.database import init_models

BRIEF = {
	"product_name": "Zephyr",
	"description": "An AI assistant that plans product launches for small teams.",
	"target_market": "B2B SaaS startups",
	"competitors": ["Acme Launch"],
}


def token(user: str) -> dict[str, str]:
	enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")
	return {"Authorization": f"Bearer {enc({'alg': 'none'})}.{enc({'sub': user})}.x"}


@pytest_asyncio.fixture
async def client():
	await init_models()
	transport = httpx.ASGITransport(app=app)
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
		yield c
	await drain_background()


async def create(client, user="alice", **overrides) -> str:
	resp = await client.post("/api/v1/launches", json={**BRIEF, **overrides}, headers=token(user))
	assert resp.status_code == 201, resp.text
	await drain_background()
	return resp.json()["launch_id"]


async def detail(client, launch_id, user="alice") -> dict:
	resp = await client.get(f"/api/v1/launches/{launch_id}", headers=token(user))
	assert resp.status_code == 200, resp.text
	return resp.json()


async def decide(client, launch_id, decision, user="alice", **extra):
	resp = await client.post(
		f"/api/v1/hitl/{launch_id}/decide", json={"decision": decision, **extra}, headers=token(user)
	)
	await drain_background()
	return resp


@pytest.mark.asyncio
async def test_full_pipeline_with_both_human_checkpoints(client) -> None:
	lid = await create(client)

	d = await detail(client, lid)
	assert d["status"] == "hitl_pending" and d["hitl_checkpoint"] == "brief_review"
	assert d["brief"]["market_data"]["competitors"]
	assert "strategy" not in d["brief"]

	pending = await client.get(f"/api/v1/hitl/{lid}/pending", headers=token("alice"))
	assert pending.json()["checkpoint"] == "brief_review"

	assert (await decide(client, lid, "approve")).json()["next_step"] == "resume_pipeline"
	d = await detail(client, lid)
	assert d["status"] == "hitl_pending" and d["hitl_checkpoint"] == "strategy_review"
	assert d["brief"]["personas"] and d["brief"]["strategy"]

	await decide(client, lid, "approve")
	d = await detail(client, lid)
	assert d["status"] == "completed" and d["hitl_pending"] is False
	assert set(d["brief"]) == {"market_data", "personas", "strategy", "content"}
	assert [p["agent_id"] for p in d["pipeline"]] == [
		"market_intelligence", "audience_insight", "launch_strategy", "content_generation",
	]
	assert all(p["status"] == "completed" and p["tokens_used"] > 0 for p in d["pipeline"])
	assert d["total_cost_usd"] > 0 and d["export_ready"] is True
	assert len(d["brief"]["content"]["ad_copy"]) >= 2

	md = await client.get(f"/api/v1/launches/{lid}/export", headers=token("alice"))
	assert md.status_code == 200 and "# Launch Brief: Zephyr" in md.text
	assert "attachment" in md.headers["content-disposition"]
	js = await client.get(f"/api/v1/launches/{lid}/export?format=json", headers=token("alice"))
	assert js.json()["summary"]["positioning"]


@pytest.mark.asyncio
async def test_edit_is_validated_persisted_and_used_downstream(client) -> None:
	lid = await create(client)

	bad = await decide(client, lid, "edit", edits={"competitors": []})
	assert bad.status_code == 422
	assert (await detail(client, lid))["hitl_checkpoint"] == "brief_review"  # still waiting

	empty = await decide(client, lid, "edit")
	assert empty.status_code == 422

	ok = await decide(client, lid, "edit", edits={"white_space": "HUMAN EDITED WHITE SPACE"})
	assert ok.status_code == 200
	d = await detail(client, lid)
	assert d["brief"]["market_data"]["white_space"] == "HUMAN EDITED WHITE SPACE"
	assert d["brief"]["market_data"]["competitors"]  # untouched fields preserved


@pytest.mark.asyncio
async def test_reject_halts_and_blocks_further_decisions(client) -> None:
	lid = await create(client)
	res = await decide(client, lid, "reject", comment="wrong market")
	assert res.json()["next_step"] == "halted"
	d = await detail(client, lid)
	assert d["status"] == "rejected" and d["hitl_pending"] is False
	assert [p["status"] for p in d["pipeline"]][1:] == ["pending"] * 3
	assert (await decide(client, lid, "approve")).status_code == 404


@pytest.mark.asyncio
async def test_stale_decision_cannot_approve_the_next_checkpoint(client) -> None:
	lid = await create(client)
	assert (await decide(client, lid, "approve", checkpoint="brief_review")).status_code == 200
	assert (await detail(client, lid))["hitl_checkpoint"] == "strategy_review"

	# A late duplicate click from the first review must not approve the strategy review blind.
	stale = await decide(client, lid, "approve", checkpoint="brief_review")
	assert stale.status_code == 409
	d = await detail(client, lid)
	assert d["status"] == "hitl_pending" and d["hitl_checkpoint"] == "strategy_review"

	assert (await decide(client, lid, "approve", checkpoint="strategy_review")).status_code == 200
	assert (await detail(client, lid))["status"] == "completed"
	# nothing left to decide
	assert (await decide(client, lid, "approve")).status_code == 404


@pytest.mark.asyncio
async def test_other_users_cannot_see_or_decide(client) -> None:
	lid = await create(client, user="alice")
	for method, path in [
		("GET", f"/api/v1/launches/{lid}"),
		("GET", f"/api/v1/launches/{lid}/export"),
		("GET", f"/api/v1/launches/{lid}/stream"),
		("GET", f"/api/v1/hitl/{lid}/pending"),
		("GET", f"/api/v1/agents/{lid}"),
		("POST", f"/api/v1/agents/{lid}/audience_insight/retry"),
	]:
		resp = await client.request(method, path, headers=token("mallory"))
		assert resp.status_code == 404, (method, path, resp.status_code)
	assert (await decide(client, lid, "reject", user="mallory")).status_code == 404
	assert (await detail(client, lid))["status"] == "hitl_pending"  # untouched
	assert (await client.get("/api/v1/launches", headers=token("mallory"))).json() == []


@pytest.mark.asyncio
async def test_input_validation_and_auth(client) -> None:
	short = await client.post("/api/v1/launches", json={**BRIEF, "description": "short"}, headers=token("a"))
	assert short.status_code == 422
	assert (await client.get("/api/v1/launches")).status_code == 401


@pytest.mark.asyncio
async def test_failed_agent_can_be_retried_and_pipeline_resumes(client, monkeypatch) -> None:
	lid = await create(client)
	real = AgentDispatcher.dispatch_result

	async def flaky(self, agent_id, payload):
		if agent_id == "audience_insight":
			raise RuntimeError("provider outage")
		return await real(self, agent_id, payload)

	monkeypatch.setattr(AgentDispatcher, "dispatch_result", flaky)
	await decide(client, lid, "approve")
	d = await detail(client, lid)
	assert d["status"] == "failed"
	failed = next(p for p in d["pipeline"] if p["agent_id"] == "audience_insight")
	assert failed["status"] == "failed" and "provider outage" in failed["error"]

	# retrying something that is not failed is refused
	assert (await client.post(f"/api/v1/agents/{lid}/market_intelligence/retry", headers=token("alice"))).status_code == 409

	monkeypatch.setattr(AgentDispatcher, "dispatch_result", real)
	assert (await client.post(f"/api/v1/agents/{lid}/audience_insight/retry", headers=token("alice"))).status_code == 200
	await drain_background()
	d = await detail(client, lid)
	assert d["status"] == "hitl_pending" and d["hitl_checkpoint"] == "strategy_review"


@pytest.mark.asyncio
async def test_unqueueable_launch_is_marked_failed_not_stuck_pending(client, monkeypatch) -> None:
	from src.apps.api.workers import runner

	def boom(_launch_id: str) -> None:
		raise ConnectionError("broker down")

	monkeypatch.setattr(runner, "enqueue_orchestrator", boom)
	lid = await create(client)
	assert (await detail(client, lid))["status"] == "failed"


def test_celery_tasks_bind_to_the_configured_app() -> None:
	from src.apps.api.workers.celery_app import celery_app
	from src.apps.api.workers.tasks import run_orchestrator_task

	assert run_orchestrator_task.app is celery_app
	assert "redis" in str(celery_app.conf.broker_url)


@pytest.mark.asyncio
async def test_post_launch_analytics_needs_completed_launch_and_real_metrics(client) -> None:
	lid = await create(client)
	url = f"/api/v1/launches/{lid}/analytics"
	body = {"metrics": {"sessions": 900, "conversions": 31, "engagement_rate": 0.4}}

	assert (await client.post(url, json=body, headers=token("alice"))).status_code == 409  # not finished
	await decide(client, lid, "approve")
	await decide(client, lid, "approve")

	assert (await client.post(url, json={"metrics": {}}, headers=token("alice"))).status_code == 422
	assert (await client.post(url, json=body, headers=token("mallory"))).status_code == 404
	ok = await client.post(url, json=body, headers=token("alice"))
	assert ok.status_code == 200 and len(ok.json()["recommendations"]) >= 3
	d = await detail(client, lid)
	assert d["brief"]["analytics"]["predicted_next_action"]
	assert d["pipeline"][-1]["agent_id"] == "analytics_feedback"
