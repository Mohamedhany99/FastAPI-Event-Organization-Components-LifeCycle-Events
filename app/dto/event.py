from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import EventType


class EventPayload(BaseModel):
    # Use internal names different from type names to avoid Pydantic field/type name clash
    event_type: EventType = Field(..., alias="type", examples=["battery_optimization_start"])
    contract_number: str = Field(..., examples=["1234"])
    event_date: date = Field(..., alias="date", examples=["2024-03-03"])
    created_at: datetime = Field(..., examples=["2024-03-03T10:00:00Z"])

    # Accept payloads using aliases ("type", "date") while exposing attributes event_type/event_date
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class EventResponse(BaseModel):
    status: Literal["accepted", "rejected"] = Field(..., examples=["accepted"])
    message: str = Field(..., examples=["Event processed successfully."])

    model_config = ConfigDict(use_enum_values=True)


