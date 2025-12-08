## P1 — Event Engine and Endpoints (Implemented)

This document summarizes all work completed in P1 to ingest events, enforce component lifecycle rules, and expose the timeline API.

### Endpoints
- `POST /event` in `app/api/routers/event.py`
  - Input: `EventPayload` (`app/dto/event.py`)
  - Output: `EventResponse` (`accepted`|`rejected`, `message`)
  - Delegates to `process_event` in `app/api/services/event_services.py`.
- `GET /contract/{contract_number}/contract_timeline` in `app/api/routers/contract.py`
  - Output: `TimelineResponse` (`app/dto/timeline.py`)
  - Delegates to `get_contract_timeline` in `app/api/services/timeline_services.py`.
- `POST /contract` routing fixed to avoid 307 redirects (now supports no trailing slash).

### Rule Engine (service layer)
- File: `app/api/services/event_services.py`
- Uses domain enums mapping (`app/domain/enums.py`) to resolve `(component, action)` from event type.
- Validations:
  - Rejects events for unknown contracts.
  - Rejects events when the component isn’t configured in the contract.
  - Enforces ordering by `created_at` (normalized to UTC-aware):
    - Start:
      - If an end exists and incoming start’s `created_at` is after that end’s `created_at` → reject (restart not allowed).
      - If a start exists and incoming start is older or equal by `created_at` → reject (don’t overwrite).
      - Otherwise, upsert start.
    - End:
      - If no prior start → reject.
      - If incoming end’s `created_at` is before/equal the start’s `created_at` → reject.
      - If an end exists and incoming end is older or equal by `created_at` → reject (don’t overwrite).
      - If `end_date < start_date` → reject.
      - Otherwise, upsert end.
- Persistence via `ComponentState` upsert:
  - `app/db/crud/component_state.py` → `get_component_state`, `upsert_component_state`, `list_component_states`.

### Timeline Service
- File: `app/api/services/timeline_services.py`
- Builds the `components` map for a given contract by reading `ComponentState` entries:
  - `{ component_type: { start, end } }`

### Database and Imports
- Models have been consolidated by the user into `app/db/models/models.py`.
- All references were refactored to import models from `app.db.models.models`:
  - `Contract` (CRUD)
  - `ComponentState` (CRUD/services)
- `app/main.py` now imports `app.db.models.models` to ensure SQLAlchemy metadata is fully populated before table creation.

### Test Suite
- Added tests for events and timelines:
  - `tests/api/test_event.py`: unknown contract, happy path, end without start, restart after end, duplicate/older events rejected.
  - `tests/api/test_timeline.py`: timeline aggregation scenario.
- Test database is ephemeral and isolated:
  - `tests/conftest.py` now uses an async in-memory SQLite (`sqlite+aiosqlite:///file::memory:?cache=shared`) and monkeypatches the app’s async engine/session.
  - Tables are created on the in-memory DB before each test client session.

### Developer Notes
- Datetime handling is normalized to UTC-aware in the event service to avoid naive/aware comparison issues.
- Error responses for `POST /event` use `EventResponse` consistently; timeline and contract errors use FastAPI `HTTPException` (404 etc.) aligned with the README.

### What’s Next (P2 Preview)
- Expand tests with more edge cases and component coverage (optional).
- Consider adding an append-only `Event` audit table for traceability and replays.
- Observability: structured logs already include key fields; consider correlation IDs if needed.


