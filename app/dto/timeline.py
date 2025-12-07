from __future__ import annotations

from datetime import date
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict

from app.domain.enums import ComponentType


class TimelineComponentWindow(BaseModel):
    start: Optional[date] = None
    end: Optional[date] = None


class TimelineResponse(BaseModel):
    contract_number: str
    components: Dict[ComponentType, TimelineComponentWindow]

    # ensure enums are serialized to their values
    model_config = ConfigDict(use_enum_values=True)


