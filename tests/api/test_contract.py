import pytest

@pytest.mark.asyncio
async def test_contract_not_found(async_client):
    res = await async_client.get("/contract/unknown")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_contract_invalid_component_422(async_client):
    res = await async_client.post("/contract", json={
        "contract_number": "C-BAD",
        "components": ["not_a_component"]
    })
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_duplicate_contract_number_conflict(async_client):
    payload = {"contract_number": "C-DUP", "components": ["energy_supply"]}
    res = await async_client.post("/contract", json=payload)
    assert res.status_code == 201
    # Duplicate
    res = await async_client.post("/contract", json=payload)
    assert res.status_code in (409, 400)