---
name: p2-tests
overview: Expand and harden the test suite with comprehensive, fast asyncio tests covering happy paths, overwrite semantics, rejections, timeline correctness, and contract validation. Minimal API tweaks only if needed for proper status codes.
todos:
  - id: add-happy-path-param-tests
    content: Parametrize happy path start/end per component in test_event.py
    status: completed
  - id: add-overwrite-tests
    content: Test newer created_at overwrites start/end; older/equal rejected
    status: completed
  - id: add-rejection-tests-unknown-unsupported
    content: Test unknown contract and unsupported component/event rejections
    status: completed
  - id: add-rejection-tests-ordering
    content: Test end before start (created_at and date) rejections
    status: completed
  - id: add-rejection-tests-restart
    content: Test start after end (restart attempt) rejection
    status: completed
  - id: add-rejection-tests-duplicates
    content: Test older duplicate (<= created_at) events are rejected
    status: completed
  - id: add-timeline-readme-tests
    content: Use README example events to assert final timeline windows
    status: completed
  - id: add-contract-validation-tests
    content: Test invalid component 422 and duplicate contract_number 409/400
    status: completed
  - id: map-duplicate-to-409
    content: Translate IntegrityError on contract create to 409 Conflict if needed
    status: completed
  - id: optional-test-reset-helper
    content: Add optional per-test schema reset/cleanup if isolation issues arise
    status: cancelled
---

# P2 — Tests (Comprehensive and Fast)

## Scope

Add thorough, high-signal tests for event processing and timelines, parameterized across components, exercising overwrite semantics and rejection rules. Ensure fast execution using the in-memory async SQLite fixture.

## Test Additions/Updates

- Update/Add: [tests/api/test_event.py](tests/api/test_event.py)
  - Happy paths (parameterized per component): start → end accepted
  - Overwrite semantics: newer created_at overwrites start/end; older/equal do not
  - Rejections:
    - Unknown contract → rejected
    - Unsupported component/event → rejected
    - End before start (by created_at and by date) → rejected
    - Start after end (restart attempt) → rejected
    - Older duplicate events (<= created_at) → rejected (no overwrite)
- Update/Add: [tests/api/test_timeline.py](tests/api/test_timeline.py)
  - Timeline correctness after realistic mixed sequences (use README example events)
  - Assert final per-component windows match expected
- Update: [tests/conftest.py](tests/conftest.py)
  - Keep single shared in-memory async SQLite (already implemented)
  - Optionally add a per-test schema reset helper if needed for isolation

## API Behavior Adjustments (minimal, only if needed for tests)

- Duplicate contract_number status code
  - Map DB unique constraint violation to 409 Conflict (or 400) during contract creation
  - File: [app/api/services/contract_services.py](app/api/services/contract_services.py) or [app/db/crud/contract.py](app/db/crud/contract.py)
- Unsupported component validation is already enforced by Pydantic validator (422)

## Example Test Shapes (concise)

```python
# tests/api/test_event.py
@pytest.mark.parametrize("component,start_type,end_type", [
    ("energy_supply", "supply_energy_start", "supply_energy_end"),
    ("battery_optimization", "battery_optimization_start", "battery_optimization_end"),
    ("heatpump_optimization", "heatpump_optimization_start", "heatpump_optimization_end"),
])
async def test_happy_path_per_component(async_client, component, start_type, end_type):
    # create contract with [component], then start/end events with increasing created_at
    ...

async def test_overwrite_newer_created_at(async_client):
    # newer start overwrites, older is rejected; same for end
    ...
```

## Performance Notes

- All tests run on in-memory DB; avoid sleeps; keep payloads minimal
- Use parametrization to reduce duplication while keeping error messages clear

## Out-of-Scope

- Event audit table and replay testing
- Load/performance testing