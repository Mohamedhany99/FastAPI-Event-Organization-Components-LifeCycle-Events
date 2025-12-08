from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db import session as db_session
from app.db.session import Base


@pytest_asyncio.fixture
async def async_client(monkeypatch):
    # Use in-memory SQLite (shared) for async tests
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///::memory::",
        connect_args={"uri": True, "check_same_thread": False},
        echo=False,
    )
    TestSessionLocal = async_sessionmaker(
        bind=test_engine, expire_on_commit=False, autoflush=False, autocommit=False
    )

    # Monkeypatch the application engine/session factory
    monkeypatch.setattr(db_session, "async_engine", test_engine, raising=True)
    monkeypatch.setattr(db_session, "AsyncSessionLocal", TestSessionLocal, raising=True)

    # Ensure tables exist on the in-memory DB
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create client with app lifespan using the patched engine/session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
