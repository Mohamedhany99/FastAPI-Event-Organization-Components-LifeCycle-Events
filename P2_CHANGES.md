## P2 — Test Suite: Event Engine, Timeline, and Validation (Implemented)

This document summarizes all testing work completed in P2. The goal was to validate the event engine (P1) and the core domain constraints (P0) with a comprehensive, deterministic, and isolated test setup.

### Highlights
- 18/18 tests passing via `poetry run pytest`.
- Full coverage of event lifecycle rules (start/end ordering, overwrite semantics, restart prevention).
- Contract and payload validation checks (supported components, unknown event types, duplicate contracts).
- Deterministic, isolated, in‑memory async SQLite for every test.

### Test Infrastructure (tests/conftest.py)
- Switched to an isolated in‑memory SQLite database per test using SQLAlchemy’s `StaticPool`:
  - `create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool, connect_args={"check_same_thread": False})`
  - `Base.metadata.drop_all()` + `Base.metadata.create_all()` executed before each test to ensure a clean schema.
- Monkeypatched the application’s `app.db.session.async_engine` and `AsyncSessionLocal` so the app under test uses the in‑memory DB during tests.
- HTTP requests are executed via `httpx.AsyncClient` with `ASGITransport(app=app)` so tests drive the real FastAPI app without an external server.

### Event Tests (tests/api/test_*)

#### Expanded event scenarios (tests/api/test_event.py)
- **Happy-path per component** (`test_happy_path_per_component`):
  - Validates start → end flows for `energy_supply`, `battery_optimization`, and `heatpump_optimization`.
- **Unknown contract** (`test_event_unknown_contract`):
  - Ensures events for non-existent contracts are rejected with `{"status":"rejected", ...}`.
- **Unsupported event type** (`test_unsupported_event_type_422`):
  - Uses an invalid `type` and validates Pydantic returns HTTP `422`.
- **Unsupported component for contract** (`test_kingpin: C-UNSUPP`) → `rejected`:
  - Contract omits a component; sending its events is rejected.
- **Ordering rules**:
  - `test_end_without_start_rejected`: cannot end before any start.
  - `test_end_before_start_by_created_at_rejected`: end event created_at must be strictly after the start’s created_at.
  - `test_older_duplicate_events_rejected`: older/equal created_at start/end events do not overwrite.
- **Restart prevention** (`test_restart_after_end_rejected`):
  - Any start event created after an end event is rejected (no restart of a terminated component).

#### Timeline scenarios (tests/api/test_timeline.py)
- **Aggregation correctness** (`test_timeline_aggregation`):
  - After a valid series of events, the timeline reflects correct start/end windows for each component present.
- **README-style scenario** (`test_timeline_from_readme_example`):
  - Mirrors the example sequence and validates:
    - Duplicate `supply_energy_start` with later `created_at` but same date does not change timeline (already set).
    - `battery_optimization_start` after an already-recorded `end` is rejected (no restart), so the original start is preserved while a later `end` can still overwrite.
    - A `heatpump_optimization_end` with a date before the start date is rejected.

### Contract Validation Tests (tests/api/test_contract.py)
- **Missing contract** (`test_contract_not_found`): returns `404`.
- **Unsupported component in payload**: HTTP `422` via Pydantic validation.
- **Duplicate contract number**: mapped to HTTP `409` by catching `IntegrityError` in `app/api/services/contract_services.py`.

### Spec Conformance Validated by Tests
- **Events are processed by `created_at`**: Later `created_at` start/end may overwrite earlier ones.
- **No end-before-start**: End must not occur before (or at the same instant as) the start’s `created_at` or earlier than the recorded start date.
- **No restart after termination**: A start event after an already-recorded end is rejected.
- **Only configured components can receive events**: Events for components not in `contract.components` are rejected.
- **Unknown contracts**: Events are rejected with a clear message.
- **Unknown event types**: Rejected at validation with HTTP `422`.

### Developer Notes
- Run tests: `pojar: poetry run pytest`
- All tests are async; `pytest-asyncio` is configured in `pyproject.toml`.
- The event processing service normalizes `created_at` to UTC-aware datetimes to avoid naive/aware comparison issues.

### Files Touched in P2
- `tests/api/test_event.*` — New/expanded scenarios for event ingestion and rule enforcement.
- `tests/api/test_timeline.*` — Timeline aggregation and README-style sequence validation.
- `tests/api/test_contract.*` — Contract validation and `404` coverage.
- `tests/conftest.py` — In‑memory async SQLite with `StaticPool`, per-test schema reset, monkeypatched DB session/engine.

All changes are test-only or validations aligned with the existing P0/P1 design. The suite now provides broad coverage over the event engine and contract validation behavior while remaining deterministic and fast.


