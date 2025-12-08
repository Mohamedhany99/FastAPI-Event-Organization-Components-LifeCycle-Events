import pytest
from datetime import date, datetime, timezone


def iso_dt(year, month, day, hour=0, minute=0, second=0):
    return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc).isoformat()


@pytest.mark.asyncio
async def test_event_unknown_contract(async_client):
    payload = {
        "type": "battery_optimization_start",
        "contract_number": "nope",
        "date": "2024-03-03",
        "created_at": iso_dt(2024, 3, 3, 10, 0, 0),
    }
    res = await async_client.post("/event", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "rejected"


@pytest.mark.asyncio
async def test_start_and_end_happy_path(async_client):
    # Create contract
    contract_payload = {
        "contract_number": "C-100",
        "components": ["battery_optimization"],
    }
    res = await async_client.post("/contract", json=contract_payload)
    assert res.status_code == 201

    # Start
    start_payload = {
        "type": "battery_optimization_start",
        "contract_number": "C-100",
        "date": "2024-03-03",
        "created_at": iso_dt(2024, 3, 3, 10, 0, 0),
    }
    res = await async_client.post("/event", json=start_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"

    # End
    end_payload = {
        "type": "battery_optimization_end",
        "contract_number": "C-100",
        "date": "2024-04-04",
        "created_at": iso_dt(2024, 4, 4, 10, 0, 0),
    }
    res = await async_client.post("/event", json=end_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_end_without_start_rejected(async_client):
    # Create contract
    contract_payload = {
        "contract_number": "C-200",
        "components": ["energy_supply"],
    }
    res = await async_client.post("/contract", json=contract_payload)
    assert res.status_code == 201

    end_payload = {
        "type": "supply_energy_end",
        "contract_number": "C-200",
        "date": "2024-01-31",
        "created_at": iso_dt(2024, 1, 31, 10, 0, 0),
    }
    res = await async_client.post("/event", json=end_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_restart_after_end_rejected(async_client):
    # Create contract
    contract_payload = {
        "contract_number": "C-300",
        "components": ["energy_supply"],
    }
    res = await async_client.post("/contract", json=contract_payload)
    assert res.status_code == 201

    start_payload = {
        "type": "supply_energy_start",
        "contract_number": "C-300",
        "date": "2024-12-01",
        "created_at": iso_dt(2024, 12, 1, 10, 0, 0),
    }
    res = await async_client.post("/event", json=start_payload)
    assert res.json()["status"] == "accepted"

    end_payload = {
        "type": "supply_energy_end",
        "contract_number": "C-300",
        "date": "2024-12-31",
        "created_at": iso_dt(2024, 12, 31, 10, 0, 0),
    }
    res = await async_client.post("/event", json=end_payload)
    assert res.json()["status"] == "accepted"

    # Restart attempt after end by created_at
    restart_payload = {
        "type": "supply_energy_start",
        "contract_number": "C-300",
        "date": "2025-01-01",
        "created_at": iso_dt(2025, 1, 1, 10, 0, 0),
    }
    res = await async_client.post("/event", json=restart_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_older_duplicate_events_rejected(async_client):
    # Create contract
    contract_payload = {
        "contract_number": "C-400",
        "components": ["battery_optimization"],
    }
    res = await async_client.post("/contract", json=contract_payload)
    assert res.status_code == 201

    # Newer start
    start_newer = {
        "type": "battery_optimization_start",
        "contract_number": "C-400",
        "date": "2024-03-10",
        "created_at": iso_dt(2024, 3, 10, 12, 0, 0),
    }
    res = await async_client.post("/event", json=start_newer)
    assert res.json()["status"] == "accepted"

    # Older start should be rejected
    start_older = {
        "type": "battery_optimization_start",
        "contract_number": "C-400",
        "date": "2024-03-03",
        "created_at": iso_dt(2024, 3, 3, 10, 0, 0),
    }
    res = await async_client.post("/event", json=start_older)
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"


