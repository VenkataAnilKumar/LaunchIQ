"""Alembic environment configuration for database migrations.

Alembic will call this script when running migrations.
It handles both online (connected to DB) and offline (SQL script generation) modes.
"""
from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from src.apps.api.models.launch import Base
import src.apps.api.models.agent  # noqa: F401 — register Agent model
import src.apps.api.models.hitl  # noqa: F401 — register HITL model
import src.apps.api.models.user  # noqa: F401 — register User model

config = context.config

# Setup Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for auto-migrations
target_metadata = Base.metadata

# Get database URL from environment
def get_sqlalchemy_url() -> str:
    """Return database URL from environment or config."""
    url = os.getenv("DATABASE_URL")
    if url is None:
        # Fallback from alembic.ini
        url = config.get_main_option("sqlalchemy.url")
    if url is None:
        raise RuntimeError("DATABASE_URL env var or sqlalchemy.url not configured")
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL script without DB connection)."""
    url = get_sqlalchemy_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connected to database)."""
    url = get_sqlalchemy_url()

    engine = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
