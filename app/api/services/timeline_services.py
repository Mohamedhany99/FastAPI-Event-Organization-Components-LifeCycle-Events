from __future__ import annotations

from typing import Dict

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.component_state import list_component_states
from app.db.crud.contract import get_contract
from app.domain.enums import ComponentType
from app.dto.timeline import TimelineComponentWindow, TimelineResponse


async def get_contract_timeline(
    db: AsyncSession, contract_number: str
) -> TimelineResponse:
    logger.info(f"Building timeline for contract {contract_number}")
    contract = await get_contract(db, contract_number)
    if contract is None:
        raise HTTPException(status_code=404, detail=f"Contract {contract_number} not found")

    states = await list_component_states(db, contract.id)
    components: Dict[ComponentType, TimelineComponentWindow] = {}
    for state in states:
        components[state.component_type] = TimelineComponentWindow(
            start=state.start_date, end=state.end_date
        )

    return TimelineResponse(contract_number=contract_number, components=components)


