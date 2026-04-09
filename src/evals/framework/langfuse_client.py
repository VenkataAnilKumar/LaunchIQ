from __future__ import annotations

from typing import Any

from src.apps.api.config import get_settings


class LangfuseClient:
	def __init__(self) -> None:
		self._client: Any | None = None
		settings = get_settings()

		if not settings.langfuse_public_key or not settings.langfuse_secret_key:
			return

		try:
			from langfuse import Langfuse

			self._client = Langfuse(
				public_key=settings.langfuse_public_key,
				secret_key=settings.langfuse_secret_key,
				host=settings.langfuse_host,
			)
		except Exception:
			# Keep eval execution resilient if Langfuse SDK is unavailable/misconfigured.
			self._client = None

	def log(
		self,
		agent_id: str,
		test_case: dict[str, Any],
		output: dict[str, Any],
		scores: dict[str, float],
	) -> None:
		if self._client is None:
			return

		try:
			trace = self._client.trace(
				name=f"eval.{agent_id}",
				input=test_case,
				output=output,
				metadata={"scores": scores},
			)
			trace_id = getattr(trace, "id", None)

			if trace_id:
				for metric, value in scores.items():
					self._client.score(
						name=metric,
						value=float(value),
						trace_id=trace_id,
					)

			flush = getattr(self._client, "flush", None)
			if callable(flush):
				flush()
		except Exception:
			# Never fail eval runs due to telemetry side effects.
			return
