"""SQLAlchemy model for agent run records."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from .launch import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    launch_id = Column(String(36), nullable=False, index=True)
    agent_id = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")
    output = Column(JSON, nullable=True)
    tokens_used = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
