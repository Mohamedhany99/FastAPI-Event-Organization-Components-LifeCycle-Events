from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ComponentType
from app.db.models.models import ComponentState


async def get_component_state(
    db: AsyncSession, contract_id, component_type: ComponentType
) -> Optional[ComponentState]:
    return await db.scalar(
        select(ComponentState).where(
            ComponentState.contract_id == contract_id,
            ComponentState.component_type == component_type,
        )
    )


async def upsert_component_state(
    db: AsyncSession,
    *,
    contract_id,
    component_type: ComponentType,
    start_date: Optional[date] = None,
    start_event_created_at: Optional[datetime] = None,
    end_date: Optional[date] = None,
    end_event_created_at: Optional[datetime] = None,
) -> ComponentState:
    """
    Basic upsert: create a row if missing; update any provided fields.
    Does NOT enforce domain rules; rule engine belongs to the service layer (P1).
    """
    try:
        state = await get_component_state(db, contract_id, component_type)
        if state is None:
            state = ComponentState(
                contract_id=contract_id, component_type=component_type
            )
            db.add(state)
            await db.flush()

        if start_date is not None:
            state.start_date = start_date
        if start_event_created_at is not None:
            state.start_event_created_at = start_event_created_at
        if end_date is not None:
            state.end_date = end_date
        if end_event_created_at is not None:
            state.end_event_created_at = end_event_created_at

        await db.commit()
        await db.refresh(state)
        return state
    except SQLAlchemyError:
        await db.rollback()
        raise


