from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Tuple

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ComponentType, EventAction, resolve_component_action
from app.db.crud.component_state import get_component_state, upsert_component_state
from app.db.crud.contract import get_contract
from app.dto.event import EventPayload, EventResponse


async def process_event(db: AsyncSession, payload: EventPayload) -> EventResponse:
    """
    Process a single event according to domain rules and persist the component state.
    Returns an accepted/rejected response; does NOT raise for domain rejections.
    """
    logger.info(f"Processing event: {payload.type} for contract {payload.contract_number}")

    contract = await get_contract(db, payload.contract_number)
    if contract is None:
        return EventResponse(status="rejected", message=f"Contract {payload.contract_number} not found.")

    component_type, action = _parse_event(payload)
    if component_type.value not in contract.components:
        return EventResponse(
            status="rejected",
            message=f"Component {component_type.value} is not configured for contract {payload.contract_number}.",
        )

    state = await get_component_state(db, contract.id, component_type)

    # Apply rules
    if action == EventAction.start:
        return await _handle_start_event(db, contract.id, component_type, state, payload.date, payload.created_at)
    else:
        return await _handle_end_event(db, contract.id, component_type, state, payload.date, payload.created_at)


def _parse_event(payload: EventPayload) -> Tuple[ComponentType, EventAction]:
    component_type, action = resolve_component_action(payload.type)
    return component_type, action


async def _handle_start_event(
    db: AsyncSession,
    contract_id,
    component_type: ComponentType,
    state,
    start_date: date,
    created_at,
) -> EventResponse:
    # Normalize to timezone-aware UTC to avoid naive/aware comparison issues
    created_at_aware = _to_aware_utc(created_at)
    # Reject restart attempts: start after a recorded end
    if state and state.end_event_created_at is not None:
        existing_end_ca = _to_aware_utc(state.end_event_created_at)
        if created_at_aware > existing_end_ca:
            return EventResponse(
                status="rejected",
                message="Start event that comes after the end event should be rejected.",
            )
        # If created_at < existing end created_at, this is an earlier start; allowed.

    # Duplicate or older start events should not overwrite
    if state and state.start_event_created_at is not None:
        existing_start_ca = _to_aware_utc(state.start_event_created_at)
        if created_at_aware <= existing_start_ca:
            return EventResponse(
                status="rejected",
                message="Start event ignored: older or equal to existing start event.",
            )

    await upsert_component_state(
        db,
        contract_id=contract_id,
        component_type=component_type,
        start_date=start_date,
        start_event_created_at=created_at_aware,
    )
    return EventResponse(status="accepted", message="Event processed successfully.")


async def _handle_end_event(
    db: AsyncSession,
    contract_id,
    component_type: ComponentType,
    state,
    end_date: date,
    created_at,
) -> EventResponse:
    # Normalize to timezone-aware UTC
    created_at_aware = _to_aware_utc(created_at)
    # Must have a start recorded before this end
    if state is None or state.start_event_created_at is None:
        return EventResponse(
            status="rejected",
            message="End event without a start event should be rejected.",
        )

    # Created_at ordering: end must come after start
    existing_start_ca = _to_aware_utc(state.start_event_created_at)
    if created_at_aware <= existing_start_ca:
        return EventResponse(
            status="rejected",
            message="End event cannot occur before start event.",
        )

    # Duplicate or older end events should not overwrite
    if state.end_event_created_at is not None:
        existing_end_ca = _to_aware_utc(state.end_event_created_at)
        if created_at_aware <= existing_end_ca:
            return EventResponse(
                status="rejected",
                message="End event ignored: older or equal to existing end event.",
            )

    # Validate date ordering (end date must not be before start date)
    if state.start_date is not None and end_date < state.start_date:
        return EventResponse(
            status="rejected",
            message="End event cannot occur before start event.",
        )

    await upsert_component_state(
        db,
        contract_id=contract_id,
        component_type=component_type,
        end_date=end_date,
        end_event_created_at=created_at_aware,
    )
    return EventResponse(status="accepted", message="Event processed successfully.")


def _to_aware_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

