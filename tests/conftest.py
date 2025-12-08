from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import session as db_session
from app.db.session import Base


@pytest_asyncio.fixture
async def async_client(monkeypatch):
    # Use a fresh in-memory SQLite DB per test with a static pool (single connection)
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    TestSessionLocal = async_sessionmaker(
        bind=test_engine, expire_on_commit=False, autoflush=False, autocommit=False
    )

    # Monkeypatch the application engine/session factory
    monkeypatch.setattr(db_session, "async_engine", test_engine, raising=True)
    monkeypatch.setattr(db_session, "AsyncSessionLocal", TestSessionLocal, raising=True)

    # Ensure a clean schema for each test
    async with test_engine.begin() as conn:
        await conn.run_sync(lambda conn: Base.metadata.drop_all(bind=conn))
        await conn.run_sync(lambda conn: Base.metadata.create_all(bind=conn))

    # Create client with app lifespan using the patched engine/session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
