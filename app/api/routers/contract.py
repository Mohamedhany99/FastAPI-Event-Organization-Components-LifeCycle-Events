from typing import Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.contract_services import (
    handle_contract_creation,
    handle_contract_deletion,
    handle_contract_retrieval,
)
from app.db.session import get_async_session
from app.dto.contract import ContractPayload, ContractResponse

router = APIRouter(
    prefix="/contract",
    responses={404: {"description": "Not found"}},
    tags=["Contract"],
)


@router.post(
    "/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED
)
async def create_contract_endpoint(
    payload: ContractPayload,
    db: AsyncSession = Depends(get_async_session),
) -> ContractResponse:
    return await handle_contract_creation(db, payload)


@router.get("/{contract_number}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
async def get_contract_endpoint(
    contract_number: str,
    db: AsyncSession = Depends(get_async_session),
) -> ContractResponse:
    return await handle_contract_retrieval(db, contract_number)


@router.delete("/{contract_number}", status_code=status.HTTP_200_OK)
async def delete_contract_endpoint(
    contract_number: str,
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, str]:
    return await handle_contract_deletion(db, contract_number)
