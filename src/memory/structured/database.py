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

# NullPool keeps connections out of reach of other event loops (Celery/Lambda).
# SQLite (local runs) is created without it so the aiosqlite default pooling applies.
_engine_kwargs: dict = {"echo": _settings.debug}
if not _settings.database_url.startswith("sqlite"):
    _engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(_settings.database_url, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an AsyncSession and closes it on exit."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_models() -> None:
    """Create all tables (local/dev convenience; production uses Alembic)."""
    import src.apps.api.models.agent
    import src.apps.api.models.hitl
    import src.apps.api.models.user  # noqa: F401
    from src.apps.api.models.launch import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
