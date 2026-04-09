"""HubSpot tool schemas."""
from __future__ import annotations

from pydantic import BaseModel


class CreateContactInput(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None


class UpdateDealInput(BaseModel):
    deal_id: str
    properties: dict[str, str]


class GetContactInput(BaseModel):
    email: str
