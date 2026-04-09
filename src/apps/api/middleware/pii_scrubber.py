"""Request-body PII scrubbing middleware."""
from __future__ import annotations

import json
import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
_CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def scrub(text: str) -> str:
	text = _EMAIL_RE.sub("[EMAIL]", text)
	text = _PHONE_RE.sub("[PHONE]", text)
	text = _CARD_RE.sub("[CARD]", text)
	text = _SSN_RE.sub("[SSN]", text)
	return text


class PIIScrubberMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
		method = request.method.upper()
		content_type = request.headers.get("content-type", "").lower()

		if method in {"POST", "PUT"} and "application/json" in content_type:
			raw = await request.body()
			if raw:
				cleaned = scrub(raw.decode("utf-8", errors="ignore"))

				# Keep JSON body parseable if scrubbed text changed structure.
				try:
					json.loads(cleaned)
				except Exception:
					cleaned = raw.decode("utf-8", errors="ignore")

				body_bytes = cleaned.encode("utf-8")

				async def receive() -> dict[str, object]:
					return {"type": "http.request", "body": body_bytes, "more_body": False}

				request._receive = receive  # type: ignore[attr-defined]

		return await call_next(request)

