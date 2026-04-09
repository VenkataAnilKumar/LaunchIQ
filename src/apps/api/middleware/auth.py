"""Clerk JWT auth middleware.

Development mode decodes JWT payload without signature verification.
Production mode verifies the JWT against Clerk's JWKS endpoint.
"""
from __future__ import annotations

import base64
import json

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.apps.api.config import get_settings


def _verify_clerk_jwt(token: str) -> dict:
	import httpx
	from jose import jwt as jose_jwt

	settings = get_settings()
	jwks_url = "https://api.clerk.com/v1/jwks"
	headers = {"Authorization": f"Bearer {settings.clerk_secret_key}"}
	response = httpx.get(jwks_url, headers=headers, timeout=10)
	response.raise_for_status()
	jwks = response.json()

	unverified = jose_jwt.get_unverified_header(token)
	key_id = unverified.get("kid")
	public_key = next(
		(k for k in jwks.get("keys", []) if k.get("kid") == key_id), None
	)
	if not public_key:
		raise ValueError("No matching public key found")

	payload = jose_jwt.decode(
		token,
		public_key,
		algorithms=["RS256"],
		audience=settings.clerk_jwt_audience or None,
	)
	return payload


def _decode_jwt_payload_without_verify(token: str) -> dict[str, object]:
	parts = token.split(".")
	if len(parts) != 3:
		raise ValueError("Invalid JWT format")
	payload_b64 = parts[1]
	payload_b64 += "=" * (-len(payload_b64) % 4)
	payload_raw = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
	return json.loads(payload_raw.decode("utf-8"))


class ClerkAuthMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):  # type: ignore[override]
		path = request.url.path
		if path in {"/api/v1/health", "/api/v1/health/ready", "/docs", "/openapi.json"}:
			return await call_next(request)

		header = request.headers.get("Authorization", "")
		if not header.startswith("Bearer "):
			return JSONResponse({"error": "missing_token"}, status_code=401)

		token = header.removeprefix("Bearer ").strip()
		settings = get_settings()
		try:
			if settings.is_production:
				payload = _verify_clerk_jwt(token)
			else:
				payload = _decode_jwt_payload_without_verify(token)
			user_id = payload.get("sub")
			if not isinstance(user_id, str) or not user_id:
				raise ValueError("JWT payload missing sub")
			request.state.user_id = user_id
		except Exception:
			return JSONResponse({"error": "invalid_token"}, status_code=401)

		return await call_next(request)

