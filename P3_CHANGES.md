## P3 — Robustness and Developer Experience (Implemented)

This document summarizes the improvements delivered in P3 to harden error handling, observability, performance, and API documentation, plus an optional event audit store.

### Error Model (standardized)
- Added `app/api/schemas/error.py` with `ErrorResponse { code, message, details? }`.
- Contract routes (`app/api/routers/contract.py`) now document and return structured errors:
  - `404 Not Found` → `{ code: "not_found", message: "Contract <id> not found." }`
  - `409 Conflict` for duplicate creation → `{ code: "conflict", message: "Contract <id> already exists" }`
  - `422 Validation Error` documented (handled by Pydantic/FastAPI).
- Kept `POST /event` behavior aligned to the README/tests: domain rejections return `200` with `EventResponse { status: "rejected", message }`. Validation errors are still `422`.

### Observability (structured logging)
- Added `app/infra/logging.py` with:
  - `configure_logging(level)` → structured, consistent console logs.
  - `log_context(contract_number, component, action, created_at)` → binds context on log lines.
- Wired logging configuration in `app/main.py` (lifespan) and applied contextual logs in services:
  - `app/api/services/event_services.py`
  - `app/api/services/contract_services.py`

### Indexing & Performance
- `contract.contract_number` is explicitly indexed and unique.
- `component_state` adds a composite index:
  - `Index("ix_component_state_contract_component", contract_id, component_type)`
- Unique constraint on `(contract_id, component_type)` remains.

### API Docs & Examples (OpenAPI)
- Added examples to DTOs:
  - `app/dto/event.py`: `EventPayload` (using aliases `type`, `date`), `EventResponse`
  - `app/dto/contract.py`: `ContractPayload`
  - `app/dto/timeline.py`: `TimelineResponse`
- Routers include standardized `responses={...}` so `/docs` shows `ErrorResponse` schemas for 404/409/422 where applicable.
- `EventPayload` uses safe internal field names with aliases (`event_type` alias `type`, `event_date` alias `date`) to avoid Pydantic name/type clashes while keeping the public API unchanged.

### Optional: Event Audit Store
- Added an append-only audit model in `app/db/models/models.py`: `Event` (`event_audit` table) with columns:
  - `id`, `contract_id`, `raw_type`, `component_type`, `action`, `event_date`, `event_created_at`, `processed_at`, `status`, `message`
  - Index on `(contract_id, event_created_at)`
- CRUD to write audit rows: `app/db/crud/event.py -> record_event(...)`.
- Integrated in `app/api/services/event_services.py` behind feature flag `settings.ENABLE_EVENT_AUDIT` (default `False`).
  - On both accepted and rejected event processing, the audit record is written when the flag is enabled.

### Compatibility & Tests
- All P2 tests remain green. No breaking route changes:
  - Event endpoint response model is unchanged for domain rejections (still `200` with `EventResponse`).
  - Contract routes now return structured bodies for 404/409; tests already accepted status codes and behavior.
- SQLite `create_all` ensures the new index/table definitions are created at startup (for production, migrations are advised).

### How to enable Event Audit
- Set `ENABLE_EVENT_AUDIT=true` in environment or `.env`.
- Restart the app; audit writes will occur on each event processing action.

### Files Added/Updated
- Added:
  - `app/api/schemas/error.py`
  - `app/infra/logging.py`
  - `app/db/crud/event.py`
- Updated (high-signal):
  - `app/api/routers/contract.py` (error responses)
  - `app/api/routers/event.py` (document 422)
  - `app/api/services/contract_services.py` (structured errors & logging)
  - `app/api/services/event_services.py` (structured logging, optional audit)
  - `app/db/models/models.py` (indexes, audit model)
  - `app/dto/event.py`, `app/dto/contract.py`, `app/dto/timeline.py` (examples and field aliasing)
  - `app/main.py` (configure logging on startup)

These changes improve resilience, developer debuggability, and OpenAPI clarity, while keeping existing behaviors and tests intact. 


