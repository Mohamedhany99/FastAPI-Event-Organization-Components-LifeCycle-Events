from typing import Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.contract_services import (
    handle_contract_creation,
    handle_contract_deletion,
    handle_contract_retrieval,
)
from app.api.services.timeline_services import get_contract_timeline
from app.db.session import get_async_session
from app.dto.contract import ContractPayload, ContractResponse
from app.dto.timeline import TimelineResponse

from app.api.schemas.error import ErrorResponse

router = APIRouter(
    prefix="/contract",
    responses={
        404: {"description": "Not Found", "model": ErrorResponse},
        409: {"description": "Conflict", "model": ErrorResponse},
        422: {"description": "Validation Error"},
    },
    tags=["Contract"],
)


@router.post(
    "", response_model=ContractResponse, status_code=status.HTTP_201_CREATED
)
async def create_contract_endpoint(
    payload: ContractPayload,
    db: AsyncSession = Depends(get_async_session),
) -> ContractResponse:
    return await handle_contract_creation(db, payload)

@router.get(
    "/{contract_number}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
)
async def get_contract_endpoint(
    contract_number: str,
    db: AsyncSession = Depends(get_async_session),
) -> ContractResponse:
    return await handle_contract_retrieval(db, contract_number)


@router.delete(
    "/{contract_number}",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
)
async def delete_contract_endpoint(
    contract_number: str,
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, str]:
    return await handle_contract_deletion(db, contract_number)


@router.get(
    "/{contract_number}/contract_timeline",
    response_model=TimelineResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
)
async def get_contract_timeline_endpoint(
    contract_number: str,
    db: AsyncSession = Depends(get_async_session),
) -> TimelineResponse:
    return await get_contract_timeline(db, contract_number)
