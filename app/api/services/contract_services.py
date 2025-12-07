from typing import Dict, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.db.crud.contract import create_contract, delete_contract, get_contract
from app.db.models.models import Contract
from app.dto.contract import ContractPayload, ContractResponse


async def handle_contract_creation(
    db: AsyncSession, payload: ContractPayload
) -> ContractResponse:
    """
    Handles the creation of a new contract.
    """
    logger.info(f"Handling contract creation for {payload.contract_number}")
    result: Contract = await create_contract(db, payload)
    result_contract: ContractResponse = ContractResponse.model_validate(result)
    logger.info(f"Successfully added a new contract with number {result_contract.contract_number}")
    return result_contract


async def handle_contract_deletion(db: AsyncSession, contract_number: str) -> Dict[str, str]:
    """
    Handles deletion of a single contract by its contract_number.
    """
    logger.info(f"Handling contract deletion for {contract_number}")
    contract = await get_contract(db, contract_number)
    if contract is None:
        raise HTTPException(status_code=404, detail=f"Contract {contract_number} not found")
    await delete_contract(db, contract_number)
    logger.info(f"Successfully deleted contract with number {contract_number}")
    return {"detail": f"Contract {contract_number} deleted successfully"}


async def handle_contract_retrieval(db: AsyncSession, contract_number: str) -> ContractResponse:
    """
    Handles retrieval of a single contract by its contract_number.
    """
    logger.info(f"Handling contract retrieval for {contract_number}")
    result: Optional[Contract] = await get_contract(db, contract_number)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Contract {contract_number} not found")
    result_contract = ContractResponse.model_validate(result)
    logger.info(f"Successfully retrieved contract with number {result_contract.contract_number}")
    return result_contract
