"""SQLAlchemy model for User (Clerk-managed identity)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String

from .launch import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(255), primary_key=True)  # Clerk sub claim
    email = Column(String(255), unique=True, nullable=False)
    plan = Column(String(50), default="free")
    integrations = Column(JSON, default=lambda: {})  # {hubspot: {...}, slack: {...}, ga4: {...}}
    created_at = Column(DateTime, default=datetime.utcnow)
