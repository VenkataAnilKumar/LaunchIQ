"""One-time utility to migrate legacy plaintext integration credentials to encrypted payloads.

Usage:
  python -m src.memory.structured.migrations.rotate_integration_credentials --dry-run
  python -m src.memory.structured.migrations.rotate_integration_credentials --apply
"""
from __future__ import annotations

import argparse
import asyncio
from typing import Any

from sqlalchemy import select

from src.apps.api.models.user import User
from src.apps.api.services.credentials_crypto import encrypt_credentials
from src.memory.structured.database import AsyncSessionLocal

INTEGRATION_NAMES = ("hubspot", "slack", "ga4")


def _extract_plain_credentials(record: Any) -> dict[str, Any] | None:
    if not isinstance(record, dict):
        return None

    if isinstance(record.get("encrypted_credentials"), str) and record.get("encrypted_credentials"):
        return None

    nested = record.get("credentials")
    if isinstance(nested, dict) and nested:
        return nested

    # Legacy flat format where the integration object itself is credentials.
    if "credentials" not in record and "status" not in record:
        return record if record else None

    return None


def _build_encrypted_record(previous: dict[str, Any], credentials: dict[str, Any]) -> dict[str, Any]:
    configured_fields = previous.get("configured_fields")
    if not isinstance(configured_fields, list):
        configured_fields = sorted(str(key) for key in credentials.keys())

    return {
        "status": previous.get("status") or "connected",
        "connected_at": previous.get("connected_at"),
        "updated_at": previous.get("updated_at"),
        "disconnected_at": previous.get("disconnected_at"),
        "last_error": previous.get("last_error"),
        "configured_fields": configured_fields,
        "encrypted_credentials": encrypt_credentials(credentials),
    }


async def migrate(*, apply: bool) -> tuple[int, int]:
    scanned = 0
    changed = 0

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

        for user in users:
            scanned += 1
            integrations = dict(user.integrations or {})
            touched = False

            for name in INTEGRATION_NAMES:
                raw = integrations.get(name)
                credentials = _extract_plain_credentials(raw)
                if not credentials:
                    continue

                previous = raw if isinstance(raw, dict) else {}
                integrations[name] = _build_encrypted_record(previous, credentials)
                touched = True

            if touched:
                changed += 1
                if apply:
                    user.integrations = integrations

        if apply and changed:
            await db.commit()

    return scanned, changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rotate/re-encrypt legacy integration credentials")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Report users that need migration")
    mode.add_argument("--apply", action="store_true", help="Apply migration updates")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scanned, changed = asyncio.run(migrate(apply=args.apply))
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] scanned_users={scanned} users_rewritten={changed}")


if __name__ == "__main__":
    main()
