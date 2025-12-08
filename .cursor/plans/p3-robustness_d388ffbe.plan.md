---
name: p3-robustness
overview: Standardize error handling and status codes, add structured logging, tighten DB indexing/perf, enrich API docs/examples, and (optionally) introduce an append-only Event audit store.
todos:
  - id: add-error-schema
    content: Create app/api/schemas/error.py with ErrorResponse model
    status: completed
  - id: wire-error-responses
    content: Standardize error responses/status codes in routers and services
    status: completed
  - id: configure-structured-logging
    content: Add app/infra/logging.py and bind context (contract, component, action, created_at)
    status: completed
  - id: apply-logging-in-services
    content: Use structured logging helpers in event/contract services
    status: completed
  - id: add-indexes-models
    content: Add/verify indexes on contract_number and (contract_id, component_type)
    status: completed
  - id: docs-examples
    content: Add OpenAPI responses and examples; ensure enums visible in schema
    status: completed
  - id: add-event-audit-model
    content: Create Event model and CRUD for append-only audit (optional)
    status: completed
  - id: integrate-audit-flag
    content: Wire event audit writes behind settings.ENABLE_EVENT_AUDIT (optional)
    status: completed
  - id: tests-verify-errors-logs
    content: Add tests for error response shape and (optionally) audit write toggling
    status: completed
---

# P3 — Robustness and Developer Experience

## Quick recap (P0–P2)

- **P0 (Core domain)**: Added enums ([app/domain/enums.py](app/domain/enums.py)), event/timeline DTOs ([app/dto/event.py](app/dto/event.py), [app/dto/timeline.py](app/dto/timeline.py)), contract component validation ([app/dto/contract.py]), ensured `contract_number` uniqueness, introduced `ComponentState` ([app/db/models/models.py]) and CRUD ([app/db/crud/component_state.py]).
- **P1 (Event engine & endpoints)**: Implemented `POST /event` ([app/api/routers/event.py](app/api/routers/event.py)) with rule engine ([app/api/services/event_services.py](app/api/services/event_services.py)), timeline endpoint on contracts ([app/api/routers/contract.py](app/api/routers/contract.py), [app/api/services/timeline_services.py](app/api/services/timeline_services.py)), wired router in [app/main.py](app/main.py). Normalized created_at comparisons to UTC-aware.
- **P2 (Tests & infra)**: Comprehensive async pytest suite ([tests/api](tests/api)), in-memory async SQLite with per-test isolation ([tests/conftest.py]). Added tests for happy paths, rejections, overwrite semantics, timeline correctness, and contract validation. Mapped duplicate contract to HTTP 409.

## Scope of P3

- Harden error model and status codes (404/422/409) consistently across endpoints.
- Add structured logging with key fields (contract_number, component, action, created_at) and consistent log formats.
- Add/verify DB indexes for common lookups: `contract.contract_number`, `(component_state.contract_id, component_type)`.
- Enrich OpenAPI docs: response models for errors, examples on endpoints, expose enums in schemas.
- (Optional) Introduce `Event` audit store for append-only event history and future replays.

## Planned Changes

### 1) Error Model & Status Codes

- Add [app/api/schemas/error.py](app/api/schemas/error.py): `ErrorResponse { code: str, message: str, details?: Any }`.
- Standardize FastAPI `responses=` on endpoints to return `ErrorResponse` with proper HTTP codes:
- 404 for not found (contracts, timelines when missing)
- 422 for validation errors (Pydantic already emits), document via `responses`
- 409 on duplicate contract creation (already handled; wire to `ErrorResponse`)
- Update services to raise `HTTPException(status_code=..., detail=ErrorResponse(...).model_dump())` where applicable.

Files to update: [app/api/routers/contract.py](app/api/routers/contract.py), [app/api/routers/event.py](app/api/routers/event.py), [app/api/services/*](app/api/services/), [app/dto/event.py](app/dto/event.py) (ensure `EventResponse` stays for 200 accepted/rejected; add `responses` block for 4xx when parsing fails).

### 2) Observability & Structured Logging

- Add [app/infra/logging.py](app/infra/logging.py) to configure `loguru` with JSON-like structured output and a helper `log_context(contract_number, component, action, created_at)` that returns a bound logger (or context manager).
- Update services to consistently log with context (at start/end, and on error/reject paths).

### 3) Indexing & Performance

- In [app/db/models/models.py](app/db/models/models.py):
- Ensure `contract.contract_number` has `unique=True` and an explicit `Index` if needed.
- Add `Index('ix_component_state_contract_component', ComponentState.contract_id, ComponentState.component_type)` (even though UniqueConstraint exists, explicit index may help some backends).
- Consider adding indexes on `(contract_id, start_event_created_at)` if queries expand (not required now; note in comments).

### 4) API Docs & Examples

- Annotate endpoints with `responses={...}` including `ErrorResponse` schemas.
- Add `example`/`examples` on `EventPayload`, `TimelineResponse`, `ContractPayload` via Pydantic `Field(..., examples=[...]) `or FastAPI `responses` examples.
- Ensure enums from [app/domain/enums.py](app/domain/enums.py) appear in the schema (already via Pydantic `Enum`); add descriptive docstrings.

### 5) Optional: Event Audit Store

- Add [app/db/models/event.py] (or extend [app/db/models/models.py]) with `Event` model: `id, contract_id FK, component_type (Enum), action (Enum), date, created_at (tz-aware), raw_type (EventType), processed_at, status (accepted|rejected), message`.
- Add [app/db/crud/event.py] with `record_event(payload, contract_id, component, action, status, message)`.
- From `process_event`, after decision, persist an audit row (guarded by `settings.ENABLE_EVENT_AUDIT: bool`).
- Add minimal tests behind a feature flag.

## Migration/Compatibility

- SQLite `create_all` will create new index/table definitions automatically. For production RDBMS, generate Alembic migrations (out of scope here).

## Deliverables

- Unified `ErrorResponse` and `responses` wiring.
- Structured logging helper and usage in services.
- Added/validated DB indexes (`contract_number`, `(contract_id, component_type)`).
- Enriched OpenAPI with examples and enum clarity.
- (Optional) `Event` audit model + CRUD + integration behind feature flag.

## Acceptance Criteria

- All existing tests (P2) remain green.
- New error responses adhere to documented `ErrorResponse` structure and correct status codes.
- Logs include contract_number, component, action, created_at for event processing paths.
- `contract_number` and `(contract_id, component_type)` indices present; no regressions.
- Docs show examples and enum values; `/docs` renders error schemas in responses.