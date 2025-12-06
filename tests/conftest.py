from typing import AsyncGenerator

import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest_asyncio.fixture
async def async_client():
    # explicitly create transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
