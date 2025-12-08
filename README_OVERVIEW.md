# Energy Operations API — Project Overview and Changes Summary

This document introduces the project at a high level and summarizes all work completed across P0–P3, including domain modeling, endpoints, event engine behavior, testing, and developer experience upgrades.

## Introduction
The Energy Operations API is a FastAPI-based service for managing utility contracts and component lifecycle events. Each contract can include multiple components; their lifecycle is expressed via start/end events which are validated and aggregated into per-contract timelines.

The project emphasizes correctness (domain rules enforced at the service layer), observability (structured logging), performance (appropriate DB indexes), and testability (comprehensive async test suite using an in-memory database).

## Objective
- Persist contracts and track component timelines via start/end events.
- Enforce ordering and lifecycle rules using event created_at timestamps and start/end dates.
- Expose endpoints to ingest events and retrieve the resulting timelines.

## Tech Stack
- Python 3.12
- FastAPI
- SQLAlchemy (async) + SQLite (dev/test)
- Pydantic v2
- Poetry
- Pytest / pytest-asyncio / httpx (ASGI transport)

## Architecture Overview
- API Routers
  - `app/api/routers/contract.py`: Contract CRUD + contract timeline endpoint
  - `app/api/routers/event.py`: Event ingestion endpoint
- Services
  - `app/api/services/contract_services.py`: Orchestrates contract create/get/delete
  - `app/api/services/event_services.py`: Event rule engine (validation, ordering, updates)
  - `app/api/services/timeline_services.py`: Builds a timeline from component states
- DTOs
  - `app/dto/contract.py`: Contract payload/response (with validation)
  - `app/dto/event.py`: Event payload/response (aliased fields to avoid naming clashes)
  - `app/dto/timeline.py`: Timeline response (per-component windows)
- DB Models & CRUD
  - `app/db/models/models.py`: `Contract`, `ComponentState`, and optional `Event` (audit)
  - `app/db/crud/contract.py`, `app/db/crud/component_state.py`, `app/db/crud/event.py`
  - `app/db/session.py`: Async engine + session factory
- Infra
  - `app/infra/logging.py`: Structured logging configuration and context binder
  - `app/api/schemas/error.py`: Standard `ErrorResponse { code, message, details? }`
  - `app/config.py`: Settings and flags (e.g., `ENABLE_EVENT_AUDIT`)

## Data Model Summary
- `Contract`:
  - `id`, `contract_number` (unique, indexed), `components` (JSON array), `created_at`
- `ComponentState` (one per `contract_id` + component):
  - `component_type` (Enum), `start_date`, `start_event_created_at`, `end_date`, `end_event_created_at`
  - Unique on `(contract_id, component_type)` and indexed on `(contract_id, component_type)`
- Optional `Event` (audit):
  - `raw_type` (EventType), `component_type`, `action`, `event_date`, `event_created_at`, `status`, `message`
  - Indexed on `(contract_id, event_created_at)`

## Domain Rules (Event Engine)
- Events are processed by `created_at` order.
- Unknown contract → rejected (domain rejection).
- Component must be configured on the contract; otherwise rejected.
- Start:
  - If an end already exists and new start has later `created_at` → reject (no restart after termination).
  - Duplicate/older/equal `created_at` start → rejected (no overwrite).
  - Otherwise set start and record `start_event_created_at`.
- End:
  - End without prior start → rejected.
  - End `created_at` must be strictly after `start_event_created_at`.
  - Duplicate/older/equal `created_at` end → rejected (no overwrite).
  - End date must not be before start date.
  - Otherwise set end and record `end_event_created_at`.

## Endpoints
- `POST /contract` → Create a contract
  - 201 on success
  - 409 on duplicate number (structured `ErrorResponse`)
  - 422 on invalid component names (Pydantic validation)
- `GET /contract/{contract_number}` → Get a contract by number
  - 200 on success; 404 (structured) if not found
- `DELETE /contract/{contract_number}` → Delete a contract
  - 200 on success; 404 (structured) if not found
- `POST /event` → Process a single event
  - 200 with `EventResponse { status: "accepted"|"rejected", message }`
  - 422 on invalid payload (Pydantic)
- `GET /contract/{contract_number}/contract_timeline` → Aggregate component windows
  - 200 on success; 404 (structured) if not found

## Error Model (Standardized)
- `app/api/schemas/error.py` defines `ErrorResponse` for non-2xx responses.
- Contract routes declare `responses={404: ErrorResponse, 409: ErrorResponse, 422: ...}`.
- Event ingestion returns domain rejections as `200` with `EventResponse` per challenge spec.

## Observability
- Structured logging with bound context fields:
  - `contract_number`, `component`, `action`, `created_at`
- Configured at startup in `app/main.py` via `configure_logging`.

## Indexing & Performance
- `contract.contract_number` is unique and indexed.
- `component_state` has a composite index on `(contract_id, component_type)`.
- Enum types use distinct names for different models to avoid DB enum clashes.

## Testing
- Async tests with an in-memory SQLite DB per test (StaticPool).
- Domain coverage includes:
  - Happy paths per component (start/end flows)
  - Ordering/overwrite (newer created_at overwrites; older/equal rejected)
  - Rejections: unknown contract, unsupported event type, unsupported component, end-before-start, restart-after-end, duplicates
  - Timeline aggregation, including a README-style scenario

Run tests:
```bash
poetry run pytest
```

## How to Run (Dev)
```bash
poetry install
poetry run uvicorn app.main:app --reload
# docs at http://localhost:8000/docs
```

## Optional Audit Store
- Enable writing append-only audit rows by setting `ENABLE_EVENT_AUDIT=true` in environment or `.env`.

## Change Logs (Detailed)
- P0: Core Domain and Constraints → `P0_CHANGES.md`
- P1: Event Engine and Endpoints → `P1_CHANGES.md`
- P2: Test Suite Enhancements → `P2_CHANGES.md`
- P3: Robustness & Developer Experience → `P3_CHANGES.md`

These changes collectively enforce the required domain rules, provide clear and consistent error semantics, improve debuggability and performance, and deliver a comprehensive, fast test suite for confidence. 

