"""SQLAlchemy model for HITL checkpoint records."""
from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, String, Text

from src.memory.structured.clock import utcnow

from .launch import Base


class HITLCheckpointRecord(Base):
    __tablename__ = "hitl_checkpoints"

    id = Column(String(36), primary_key=True)
    launch_id = Column(String(36), nullable=False, index=True)
    checkpoint = Column(String(100), nullable=False)
    agent_id = Column(String(100), nullable=False)
    output_preview = Column(JSON, nullable=False)
    decision = Column(String(50), nullable=True)  # approve / edit / reject
    edits = Column(JSON, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    resolved_at = Column(DateTime, nullable=True)
