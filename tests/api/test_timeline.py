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


