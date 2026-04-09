"""Repository for User records and integration credential storage."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.api.models.user import User
from src.apps.api.services.credentials_crypto import decrypt_credentials, encrypt_credentials

INTEGRATION_NAMES = ("hubspot", "slack", "ga4")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_integration_record(value: Any) -> dict[str, Any]:
    if isinstance(value, dict) and "encrypted_credentials" in value:
        encrypted_credentials = value.get("encrypted_credentials")
        has_encrypted = isinstance(encrypted_credentials, str) and bool(encrypted_credentials.strip())
        configured_fields = value.get("configured_fields")
        if not isinstance(configured_fields, list):
            configured_fields = []
        return {
            "status": "connected" if has_encrypted else "disconnected",
            "connected_at": value.get("connected_at"),
            "updated_at": value.get("updated_at"),
            "disconnected_at": value.get("disconnected_at"),
            "last_error": value.get("last_error"),
            "configured_fields": configured_fields,
            "credentials": {},
            "encrypted_credentials": encrypted_credentials if has_encrypted else None,
        }

    if isinstance(value, dict) and "credentials" in value:
        credentials = value.get("credentials")
        if not isinstance(credentials, dict):
            credentials = {}
        configured_fields = value.get("configured_fields")
        if not isinstance(configured_fields, list):
            configured_fields = sorted(str(key) for key in credentials.keys())
        return {
            "status": "connected" if credentials else "disconnected",
            "connected_at": value.get("connected_at"),
            "updated_at": value.get("updated_at"),
            "disconnected_at": value.get("disconnected_at"),
            "last_error": value.get("last_error"),
            "configured_fields": configured_fields,
            "credentials": credentials,
            "encrypted_credentials": None,
        }

    if isinstance(value, dict):
        credentials = value
        return {
            "status": "connected" if credentials else "disconnected",
            "connected_at": None,
            "updated_at": None,
            "disconnected_at": None,
            "last_error": None,
            "configured_fields": sorted(str(key) for key in credentials.keys()),
            "credentials": credentials,
            "encrypted_credentials": None,
        }

    return {
        "status": "disconnected",
        "connected_at": None,
        "updated_at": None,
        "disconnected_at": None,
        "last_error": None,
        "configured_fields": [],
        "credentials": {},
        "encrypted_credentials": None,
    }


def _to_public_metadata(name: str, record: dict[str, Any]) -> dict[str, Any]:
    credentials = record.get("credentials")
    encrypted_credentials = record.get("encrypted_credentials")
    has_credentials = bool(
        (isinstance(credentials, dict) and len(credentials) > 0)
        or (isinstance(encrypted_credentials, str) and bool(encrypted_credentials.strip()))
    )
    connected = bool(has_credentials and record.get("status") == "connected")
    return {
        "name": name,
        "status": "connected" if connected else "disconnected",
        "connected": connected,
        "has_credentials": has_credentials,
        "connected_at": record.get("connected_at"),
        "updated_at": record.get("updated_at"),
        "disconnected_at": record.get("disconnected_at"),
        "last_error": record.get("last_error"),
        "configured_fields": record.get("configured_fields") or [],
    }


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_or_update(self, user_id: str, email: str, data: dict[str, Any]) -> User:
        existing = await self.get(user_id)
        if existing is None:
            user = User(user_id=user_id, email=email, integrations=data.get("integrations", {}))
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user

        await self.db.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(email=email, integrations=data.get("integrations", existing.integrations or {}))
        )
        await self.db.commit()
        refreshed = await self.get(user_id)
        if refreshed is None:
            raise RuntimeError("Failed to refresh user after update")
        return refreshed

    async def update_integrations(
        self,
        user_id: str,
        integration_name: str,
        credentials: dict[str, Any],
    ) -> None:
        now = _utc_now_iso()
        encrypted_credentials = encrypt_credentials(credentials)
        user = await self.get(user_id)
        existing_record = _coerce_integration_record(
            (user.integrations or {}).get(integration_name) if user else None
        )
        next_record = {
            "status": "connected",
            "connected_at": existing_record.get("connected_at") or now,
            "updated_at": now,
            "disconnected_at": None,
            "last_error": None,
            "configured_fields": sorted(str(key) for key in credentials.keys()),
            "encrypted_credentials": encrypted_credentials,
        }

        if user is None:
            user = User(
                user_id=user_id,
                email=f"{user_id}@placeholder.local",
                integrations={integration_name: next_record},
            )
            self.db.add(user)
            await self.db.commit()
            return

        integrations = dict(user.integrations or {})
        integrations[integration_name] = next_record
        await self.db.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(integrations=integrations)
        )
        await self.db.commit()

    async def remove_integration(self, user_id: str, integration_name: str) -> None:
        user = await self.get(user_id)
        if user is None:
            return

        now = _utc_now_iso()
        integrations = dict(user.integrations or {})
        existing_record = _coerce_integration_record(integrations.get(integration_name))
        integrations[integration_name] = {
            **existing_record,
            "status": "disconnected",
            "updated_at": now,
            "disconnected_at": now,
            "credentials": {},
            "encrypted_credentials": None,
        }
        await self.db.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(integrations=integrations)
        )
        await self.db.commit()

    async def list_integration_metadata(self, user_id: str) -> dict[str, dict[str, Any]]:
        user = await self.get(user_id)
        stored_integrations = dict(user.integrations or {}) if user else {}
        metadata: dict[str, dict[str, Any]] = {}

        for name in INTEGRATION_NAMES:
            record = _coerce_integration_record(stored_integrations.get(name))
            metadata[name] = _to_public_metadata(name, record)

        return metadata

    async def set_integration_error(self, user_id: str, integration_name: str, error_message: str | None) -> None:
        user = await self.get(user_id)
        if user is None:
            return

        integrations = dict(user.integrations or {})
        record = _coerce_integration_record(integrations.get(integration_name))
        record["last_error"] = error_message
        record["updated_at"] = _utc_now_iso()
        integrations[integration_name] = record

        await self.db.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(integrations=integrations)
        )
        await self.db.commit()

    async def get_integration_credentials(self, user_id: str, integration_name: str) -> dict[str, Any] | None:
        user = await self.get(user_id)
        if user is None:
            return None

        record = _coerce_integration_record((user.integrations or {}).get(integration_name))
        encrypted_credentials = record.get("encrypted_credentials")
        if isinstance(encrypted_credentials, str) and encrypted_credentials.strip():
            return decrypt_credentials(encrypted_credentials)

        credentials = record.get("credentials")
        if isinstance(credentials, dict) and credentials:
            return credentials

        return None