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
@pytest.mark.parametrize(
    "component,start_type,end_type,start_date,end_date",
    [
        ("energy_supply", "supply_energy_start", "supply_energy_end", "2024-01-01", "2024-01-31"),
        ("battery_optimization", "battery_optimization_start", "battery_optimization_end", "2024-03-03", "2024-04-04"),
        ("heatpump_optimization", "heatpump_optimization_start", "heatpump_optimization_end", "2025-03-03", "2025-04-04"),
    ],
)
async def test_happy_path_per_component(async_client, component, start_type, end_type, start_date, end_date):
    contract_payload = {"contract_number": f"HAPPY-{component}", "components": [component]}
    res = await async_client.post("/contract", json=contract_payload)
    assert res.status_code == 201

    res = await async_client.post("/event", json={
        "type": start_type, "contract_number": f"HAPPY-{component}", "date": start_date, "created_at": iso_dt(2024, 1, 1, 9)
    })
    assert res.status_code == 200 and res.json()["status"] == "accepted"

    res = await async_client.post("/event", json={
        "type": end_type, "contract_number": f"HAPPY-{component}", "date": end_date, "created_at": iso_dt(2024, 12, 31, 9)
    })
    assert res.status_code == 200 and res.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_unsupported_event_type_422(async_client):
    # Pydantic should reject unknown event type
    payload = {
        "type": "unknown_event",
        "contract_number": "ANY",
        "date": "2024-01-01",
        "created_at": iso_dt(2024, 1, 1, 1),
    }
    res = await async_client.post("/event", json=payload)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_unsupported_component_for_contract_rejected(async_client):
    # Contract has only energy_supply; battery_* event should be rejected
    res = await async_client.post("/contract", json={
        "contract_number": "C-UNSUPP", "components": ["energy_supply"]
    })
    assert res.status_code == 201
    res = await async_client.post("/event", json={
        "type": "battery_optimization_start",
        "contract_number": "C-UNSUPP",
        "date": "2024-03-03",
        "created_at": iso_dt(2024, 3, 3, 10),
    })
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_end_before_start_by_created_at_rejected(async_client):
    res = await async_client.post("/contract", json={
        "contract_number": "C-ORD-1", "components": ["energy_supply"]
    })
    assert res.status_code == 201
    # Start at later created_at
    res = await async_client.post("/event", json={
        "type": "supply_energy_start", "contract_number": "C-ORD-1",
        "date": "2024-12-01", "created_at": iso_dt(2024, 12, 10, 10),
    })
    assert res.json()["status"] == "accepted"
    # End with earlier created_at → reject
    res = await async_client.post("/event", json={
        "type": "supply_energy_end", "contract_number": "C-ORD-1",
        "date": "2024-12-31", "created_at": iso_dt(2024, 12, 9, 9),
    })
    assert res.status_code == 200 and res.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_end_before_start_by_date_rejected(async_client):
    res = await async_client.post("/contract", json={
        "contract_number": "C-ORD-2", "components": ["energy_supply"]
    })
    assert res.status_code == 201
    res = await async_client.post("/event", json={
        "type": "supply_energy_start", "contract_number": "C-ORD-2",
        "date": "2024-12-10", "created_at": iso_dt(2024, 12, 10, 10),
    })
    assert res.json()["status"] == "accepted"
    # End date before start date; created_at later so only date rule triggers
    res = await async_client.post("/event", json={
        "type": "supply_energy_end", "contract_number": "C-ORD-2",
        "date": "2024-12-01", "created_at": iso_dt(2024, 12, 11, 10),
    })
    assert res.status_code == 200 and res.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_overwrite_newer_created_at_updates_state(async_client):
    res = await async_client.post("/contract", json={
        "contract_number": "C-OVR-1", "components": ["battery_optimization"]
    })
    assert res.status_code == 201
    # Initial start
    res = await async_client.post("/event", json={
        "type": "battery_optimization_start", "contract_number": "C-OVR-1",
        "date": "2024-03-03", "created_at": iso_dt(2024, 3, 3, 9),
    })
    assert res.json()["status"] == "accepted"
    # Newer start overwrites
    res = await async_client.post("/event", json={
        "type": "battery_optimization_start", "contract_number": "C-OVR-1",
        "date": "2024-03-15", "created_at": iso_dt(2024, 3, 15, 9),
    })
    assert res.json()["status"] == "accepted"
    # Confirm timeline shows overwritten start
    res = await async_client.get("/contract/C-OVR-1/contract_timeline")
    data = res.json()
    assert data["components"]["battery_optimization"]["start"] == "2024-03-15"

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


