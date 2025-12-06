from datetime import datetime
from enum import Enum

from pydantic import UUID4, BaseModel, ConfigDict


class ContractPayload(BaseModel):
    contract_number: str
    components: list[str]


class ContractResponse(BaseModel):
    id: UUID4
    contract_number: str
    components: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
