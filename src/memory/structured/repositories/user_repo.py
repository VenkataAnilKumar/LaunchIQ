"""Repository for User records and integration credential storage."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.api.models.user import User


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
        user = await self.get(user_id)
        if user is None:
            user = User(
                user_id=user_id,
                email=f"{user_id}@placeholder.local",
                integrations={integration_name: credentials},
            )
            self.db.add(user)
            await self.db.commit()
            return

        integrations = dict(user.integrations or {})
        integrations[integration_name] = credentials
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

        integrations = dict(user.integrations or {})
        integrations.pop(integration_name, None)
        await self.db.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(integrations=integrations)
        )
        await self.db.commit()