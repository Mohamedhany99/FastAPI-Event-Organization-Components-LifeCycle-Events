import pytest

@pytest.mark.asyncio
async def test_contract_not_found(async_client):
    res = await async_client.get("/contract/unknown")
    assert res.status_code == 404