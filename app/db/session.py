from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Async engine and sessionmaker
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    **settings.ASYNC_SQLALCHEMY_ENGINE_OPTIONS,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
