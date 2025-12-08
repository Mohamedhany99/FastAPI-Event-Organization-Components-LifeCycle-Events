from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.event_services import process_event
from app.db.session import get_async_session
from app.dto.event import EventPayload, EventResponse


router = APIRouter(tags=["Events"])


@router.post("/event", response_model=EventResponse, status_code=status.HTTP_200_OK)
async def post_event(
    payload: EventPayload, db: AsyncSession = Depends(get_async_session)
) -> EventResponse:
    return await process_event(db, payload)


