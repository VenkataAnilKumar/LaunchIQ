"""Credential validation helpers for third-party integrations."""
from __future__ import annotations

import json
from typing import Any

import httpx


class IntegrationValidationError(ValueError):
    pass


async def validate_integration_credentials(
    integration_name: str,
    credentials: dict[str, Any],
) -> tuple[bool, str]:
    if integration_name == "hubspot":
        return await _validate_hubspot(credentials)
    if integration_name == "slack":
        return await _validate_slack(credentials)
    if integration_name == "ga4":
        return _validate_ga4(credentials)
    raise IntegrationValidationError(f"Unsupported integration: {integration_name}")


async def _validate_hubspot(credentials: dict[str, Any]) -> tuple[bool, str]:
    token = str(credentials.get("access_token", "")).strip()
    if not token:
        return False, "HubSpot access_token is required"

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            "https://api.hubapi.com/integrations/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code == 200:
        return True, "HubSpot credentials are valid"
    return False, f"HubSpot validation failed ({response.status_code})"


async def _validate_slack(credentials: dict[str, Any]) -> tuple[bool, str]:
    token = str(credentials.get("bot_token", "")).strip()
    if not token:
        return False, "Slack bot_token is required"

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code != 200:
        return False, f"Slack validation failed ({response.status_code})"

    payload = response.json()
    if bool(payload.get("ok")):
        return True, "Slack credentials are valid"

    error = str(payload.get("error") or "unknown_error")
    return False, f"Slack validation failed ({error})"


def _validate_ga4(credentials: dict[str, Any]) -> tuple[bool, str]:
    property_id = str(credentials.get("property_id", "")).strip()
    service_account_json = str(credentials.get("service_account_json", "")).strip()

    if not property_id:
        return False, "GA4 property_id is required"
    if not property_id.isdigit():
        return False, "GA4 property_id must be numeric"
    if not service_account_json:
        return False, "GA4 service_account_json is required"

    try:
        parsed = json.loads(service_account_json)
    except json.JSONDecodeError:
        return False, "GA4 service_account_json must be valid JSON"

    required = {"client_email", "private_key", "project_id"}
    missing = sorted(key for key in required if not isinstance(parsed.get(key), str) or not parsed.get(key))
    if missing:
        return False, f"GA4 service account JSON is missing: {', '.join(missing)}"

    return True, "GA4 credentials look valid"
