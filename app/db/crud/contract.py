from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.contract import Contract
from app.dto.contract import ContractPayload


async def create_contract(db: AsyncSession, payload: ContractPayload) -> Contract:
    contract = Contract(
        contract_number=payload.contract_number,
        components=payload.components,
    )
    db.add(contract)

    try:
        await db.commit()
        await db.refresh(contract)
    except SQLAlchemyError:
        await db.rollback()
        raise

    return contract


async def delete_contract(db: AsyncSession, contract_number: str) -> None:
    try:
        contract = await db.scalar(
            select(Contract).where(Contract.contract_number == contract_number)
        )

        if not contract:
            return

        await db.delete(contract)
        await db.commit()

    except SQLAlchemyError:
        await db.rollback()
        raise


async def get_contract(db: AsyncSession, contract_number: str) -> Optional[Contract]:
    return await db.scalar(select(Contract).where(Contract.contract_number == contract_number))
