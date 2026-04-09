"""HubSpot SDK auth helper."""
from __future__ import annotations

from typing import Any


def get_hubspot_client(api_key: str) -> Any:
    if not api_key:
        raise ValueError("Missing HubSpot API key")
    try:
        from hubspot import HubSpot
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("hubspot-api-client SDK is not installed") from exc

    return HubSpot(access_token=api_key)
