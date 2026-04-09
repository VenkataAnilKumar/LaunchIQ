"""Async SQLAlchemy engine and session factory.

Uses NullPool so Lambda functions never share pooled connections across
cold-start boundaries. FastAPI routes obtain a session via get_db().
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.apps.api.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.database_url,
    poolclass=NullPool,
    echo=_settings.debug,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an AsyncSession and closes it on exit."""
    async with AsyncSessionLocal() as session:
        yield session
