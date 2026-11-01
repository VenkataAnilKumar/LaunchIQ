"""UTC clock for the structured layer.

Columns are timezone-naive ``DateTime``; asyncpg rejects aware datetimes for those, so
this returns the current UTC time *without* tzinfo (replacement for deprecated utcnow()).
"""
from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
