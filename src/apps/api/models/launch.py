"""SQLAlchemy model for the Launch entity.

Also defines Base (DeclarativeBase) — all other models import from here.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class LaunchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    HITL_PENDING = "hitl_pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Launch(Base):
    __tablename__ = "launches"

    launch_id = Column(String(36), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    status = Column(String(50), default="pending")
    product_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    target_market = Column(String(255), nullable=False)
    competitors = Column(JSON, default=lambda: [])
    launch_date = Column(String(50), nullable=True)
    brief_output = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
