"""Initial schema migration for LaunchIQ.

Creates tables: launches, agent_runs, hitl_checkpoints, users
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# Revision IDs
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables."""
    # launches table
    op.create_table(
        "launches",
        sa.Column("launch_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("target_market", sa.String(255), nullable=False),
        sa.Column("competitors", sa.JSON, nullable=True),
        sa.Column("launch_date", sa.String(50), nullable=True),
        sa.Column("brief_output", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("launch_id"),
        sa.Index("ix_launches_user_id", "user_id"),
    )

    # agent_runs table
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("launch_id", sa.String(36), nullable=False),
        sa.Column("agent_id", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("output", sa.JSON, nullable=True),
        sa.Column("tokens_used", sa.Integer, server_default="0"),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Index("ix_agent_runs_launch_id", "launch_id"),
    )

    # hitl_checkpoints table
    op.create_table(
        "hitl_checkpoints",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("launch_id", sa.String(36), nullable=False),
        sa.Column("checkpoint", sa.String(100), nullable=False),
        sa.Column("agent_id", sa.String(100), nullable=False),
        sa.Column("output_preview", sa.JSON, nullable=False),
        sa.Column("decision", sa.String(50), nullable=True),
        sa.Column("edits", sa.JSON, nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_hitl_checkpoints_launch_id", "launch_id"),
    )

    # users table
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("plan", sa.String(50), server_default="free"),
        sa.Column("integrations", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("users")
    op.drop_table("hitl_checkpoints")
    op.drop_table("agent_runs")
    op.drop_table("launches")
