from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.models import Event
from app.domain.enums import ComponentType, EventAction, EventType as EventTypeEnum


async def record_event(
    db: AsyncSession,
    *,
    contract_id: Optional[str],
    raw_type: EventTypeEnum,
    component_type: Optional[ComponentType],
    action: Optional[EventAction],
    event_date: Optional[date],
    event_created_at: Optional[datetime],
    status: str,
    message: Optional[str] = None,
) -> Event:
    evt = Event(
        contract_id=contract_id,
        raw_type=raw_type,
        component_type=component_type,
        action=action,
        event_date=event_date,
        event_created_at=event_created_at,
        status=status,
        message=message,
    )
    db.add(evt)
    try:
        await db.commit()
        await db.refresh(evt)
        return evt
    except SQLAlchemyError:
        await db.rollback()
        raise


