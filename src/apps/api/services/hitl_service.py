"""HITL service business logic."""
from __future__ import annotations

from typing import Any

from src.memory.short_term.hitl_state import HITLStateStore
from src.memory.short_term.session_store import SessionStore


class HITLService:
	async def get_pending(self, launch_id: str) -> dict[str, Any] | None:
		store = HITLStateStore()
		return await store.get_pending(launch_id)

	async def resolve(
		self,
		launch_id: str,
		decision: str,
		edits: dict[str, Any] | None,
		comment: str | None,
	) -> dict[str, Any] | None:
		state_store = HITLStateStore()
		pending = await state_store.get_pending(launch_id)
		if pending is None:
			return None

		await state_store.resolve(launch_id, decision, edits)

		session = SessionStore()
		event = {
			"type": "hitl_resolved",
			"launch_id": launch_id,
			"decision": decision,
			"edits": edits,
			"comment": comment,
		}
		await session.publish(f"launch:{launch_id}:hitl", event)
		await session.publish(f"launch:{launch_id}:events", event)

		next_step = "halted" if decision == "reject" else "resume_pipeline"
		return {"next_step": next_step}


def get_hitl_service() -> HITLService:
	return HITLService()

