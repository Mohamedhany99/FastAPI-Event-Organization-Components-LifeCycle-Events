from typing import Dict, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.api.schemas.error import ErrorResponse

from app.db.crud.contract import create_contract, delete_contract, get_contract
from app.db.models.models import Contract
from app.dto.contract import ContractPayload, ContractResponse
from app.infra.logging import log_context


async def handle_contract_creation(
    db: AsyncSession, payload: ContractPayload
) -> ContractResponse:
    """
    Handles the creation of a new contract.
    """
    log = log_context(contract_number=payload.contract_number)
    log.info("Handling contract creation")
    try:
        result: Contract = await create_contract(db, payload)
        result_product = ContractResponse.model_validate(result)
        log.info("Contract created")
        return result_product
    except IntegrityError:
        logger.warning(f"Duplicate contract number detected: {payload.contract_number}")
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(code="conflict", message=f"Contract {payload.contract_number} already exists").model_dump(),
        )
    except SQLAlchemyError:
        # Bubble up as 500 by default
        raise


async def handle_contract_deletion(db: AsyncSession, contract_number: str) -> Dict[str, str]:
    """
    Handles deletion of a single contract by its contract_number.
    """
    log = log_context(contract_number=contract_number)
    log.info("Handling contract deletion")
    contract = await get_contract(db, contract_number)
    if contract is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(code="not_found", message=f"Contract {contract_number} not found.").model_dump(),
        )
    await delete_contract(db, contract_number)
    log.info("Contract deleted")
    return {"detail": f"Contract {contract_number} deleted successfully"}


async def handle_contract_retrieval(db: AsyncSession, contract_number: str) -> ContractResponse:
    """
    Handles retrieval of a single contract by its contract_number.
    """
    log = log_context(contract_number=contract_number)
    log.info("Handling contract retrieval")
    result: Optional[Contract] = await get_contract(db, contract_number)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(code="not_found", message=f"Contract {contract_number} not found.").model_dump(),
        )
    result_contract = ContractResponse.model_validate(result)
    log.info("Contract retrieved")
    return result_contract
