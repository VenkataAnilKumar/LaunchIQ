"""Add per-run cost tracking to agent_runs."""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "002_agent_run_cost"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("agent_runs", sa.Column("cost_usd", sa.Float, server_default="0"))


def downgrade() -> None:
    op.drop_column("agent_runs", "cost_usd")
