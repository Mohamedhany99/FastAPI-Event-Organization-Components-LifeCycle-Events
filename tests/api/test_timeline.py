import pytest
from datetime import datetime, timezone


def iso_dt(year, month, day, hour=0, minute=0, second=0):
    return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc).isoformat()


@pytest.mark.asyncio
async def test_timeline_aggregation(async_client):
    # Create contract
    contract_payload = {
        "contract_number": "C-TL-1",
        "components": ["energy_supply", "battery_optimization"],
    }
    res = await async_client.post("/contract", json=contract_payload)
    assert res.status_code == 201

    # Events
    events = [
        {"type": "supply_energy_start", "date": "2024-12-01", "created_at": iso_dt(2024, 12, 1, 9)},
        {"type": "supply_energy_end", "date": "2024-12-31", "created_at": iso_dt(2024, 12, 31, 9)},
        {"type": "battery_optimization_start", "date": "2024-03-03", "created_at": iso_dt(2024, 3, 3, 10)},
    ]
    for e in events:
        payload = {"contract_number": "C-TL-1", **e}
        res = await async_client.post("/event", json=payload)
        assert res.status_code == 200
        assert res.json()["status"] in ("accepted",)  # all should accept

    # Fetch timeline
    res = await async_client.get("/contract/C-TL-1/contract_timeline")
    assert res.status_code == 200
    data = res.json()
    assert data["contract_number"] == "C-TL-1"
    comps = data["components"]
    assert comps["energy_supply"]["start"] == "2024-12-01"
    assert comps["energy_supply"]["end"] == "2024-12-31"
    assert comps["battery_optimization"]["start"] == "2024-03-03"
    assert comps["battery_optimization"]["end"] is None


@pytest.mark.asyncio
async def test_timeline_from_readme_example(async_client):
    # Create contract
    res = await async_client.post("/contract", json={
        "contract_number": "1234",
        "components": ["energy_supply", "battery_optimization", "heatpump_optimization"],
    })
    assert res.status_code == 201

    # Example-like events (with created_at to enforce ordering)
    events = [
        {"type": "supply_energy_start", "contract_number": "1234", "date": "2024-12-01", "created_at": iso_dt(2024, 12, 1, 9)},
        {"type": "supply_energy_end", "contract_number": "1234", "date": "2024-12-31", "created_at": iso_dt(2024, 12, 31, 9)},
        {"type": "battery_optimization_start", "contract_number": "1234", "date": "2024-03-03", "created_at": iso_dt(2024, 3, 3, 9)},
        {"type": "battery_optimization_end", "contract_number": "1234", "date": "2024-04-04", "created_at": iso_dt(2024, 4, 4, 9)},
        {"type": "heatpump_optimization_start", "contract_number": "1234", "date": "2025-03-03", "created_at": iso_dt(2025, 3, 3, 9)},
        {"type": "heatpump_optimization_end", "contract_number": "1234", "date": "2025-04-04", "created_at": iso_dt(2025, 4, 4, 9)},
        # This end is before start date -> should be rejected by date rule
        {"type": "battery_optimization_end", "contract_number": "1234", "date": "2024-02-01", "created_at": iso_dt(2025, 5, 1, 9)},
        # Duplicate start for energy_supply -> equal date, later created_at; allowed overwrite (no visible change)
        {"type": "supply_energy_start", "contract_number": "1234", "date": "2024-12-01", "created_at": iso_dt(2025, 5, 2, 9)},
        # Unknown contract should be rejected by service; but Pydantic won't validate here since contract_number exists; we skip adding 9999 here
        # Overwrite battery start/end with newer created_at
        {"type": "battery_optimization_start", "contract_number": "1234", "date": "2024-03-15", "created_at": iso_dt(2025, 5, 3, 9)},
        {"type": "battery_optimization_end", "contract_number": "1234", "date": "2024-04-15", "created_at": iso_dt(2025, 5, 4, 9)},
        # Heatpump end with earlier date than start -> reject
        {"type": "heatpump_optimization_end", "contract_number": "1234", "date": "2025-02-01", "created_at": iso_dt(2025, 5, 5, 9)},
    ]
    for evt in events:
        res = await async_client.post("/event", json=evt)
        assert res.status_code == 200

    res = await async_client.get("/contract/1234/contract_timeline")
    assert res.status_code == 200
    data = res.json()
    comps = data["components"]
    assert comps["energy_supply"]["start"] == "2024-12-01"
    assert comps["energy_supply"]["end"] == "2024-12-31"
    # Start remains the original, since a start event created after an end is rejected
    assert comps["battery_optimization"]["start"] == "2024-03-03"
    assert comps["battery_optimization"]["end"] == "2024-04-15"
    assert comps["heatpump_optimization"]["start"] == "2025-03-03"
    assert comps["heatpump_optimization"]["end"] == "2025-04-04"

