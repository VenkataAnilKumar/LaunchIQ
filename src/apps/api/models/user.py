"""SQLAlchemy model for User (Clerk-managed identity)."""
from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, String

from src.memory.structured.clock import utcnow

from .launch import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(255), primary_key=True)  # Clerk sub claim
    email = Column(String(255), unique=True, nullable=False)
    plan = Column(String(50), default="free")
    integrations = Column(JSON, default=dict)  # {hubspot: {...}, slack: {...}, ga4: {...}}
    created_at = Column(DateTime, default=utcnow)
