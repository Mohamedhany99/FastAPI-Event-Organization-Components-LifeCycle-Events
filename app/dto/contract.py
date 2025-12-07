from datetime import datetime
from typing import Iterable, Union

from pydantic import UUID4, BaseModel, ConfigDict, field_validator
from app.domain.enums import ComponentType


class ContractPayload(BaseModel):
    contract_number: str
    components: list[str]

    @field_validator("components")
    @classmethod
    def validate_components_supported(
        cls, components: Iterable[Union[str, ComponentType]]
    ) -> list[str]:
        normalized: list[str] = []
        for comp in components:
            if isinstance(comp, ComponentType):
                normalized.append(comp.value)
                continue
            # comp is a string: must be one of ComponentType values
            try:
                ct = ComponentType(comp)
            except ValueError as exc:
                allowed = ", ".join([c.value for c in ComponentType])
                raise ValueError(
                    f"Unsupported component '{comp}'. Allowed: {allowed}"
                ) from exc
            normalized.append(ct.value)
        return normalized


class ContractResponse(BaseModel):
    id: UUID4
    contract_number: str
    components: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
