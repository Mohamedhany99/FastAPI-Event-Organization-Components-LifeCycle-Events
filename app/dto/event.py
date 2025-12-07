from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.domain.enums import EventType


class EventPayload(BaseModel):
    type: EventType
    contract_number: str
    date: date
    created_at: datetime


class EventResponse(BaseModel):
    status: Literal["accepted", "rejected"]
    message: str

    model_config = ConfigDict(use_enum_values=True)


