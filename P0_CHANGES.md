# P0 — Core Domain and Constraints (Implemented)

This document summarizes all changes introduced in P0 to establish the core domain, DTOs, and persistence constraints for component lifecycle tracking.

## Overview
- Introduced strong domain types (enums) for components, actions, and event types.
- Added DTOs for events and timelines with validation-friendly schemas.
- Validated contract components against the supported set.
- Enforced uniqueness of `contract_number` at the database model level.
- Added `ComponentState` persistence to store per-component start/end state.
- Added basic CRUD helpers for `ComponentState` (no rule engine yet).

No runtime behavior changes to existing endpoints were made in P0; new endpoints and rule engine will arrive in P1.

---

## Added Files
- `app/domain/enums.py`
  - `ComponentType`: `energy_supply`, `battery_optimization`, `heatpump_optimization`
  - `EventAction`: `start`, `end`
  - `EventType`: full set of supported event types
  - `resolve_component_action(event_type)` helper to map event type → `(component, action)`

- `app/dto/event.py`
  - `EventPayload`: `type`, `contract_number`, `date`, `created_at`
  - `EventResponse`: `status` (`accepted`|`rejected`), `message`

- `app/dto/timeline.py`
  - `TimelineComponentWindow`: `{ start?: date, end?: date }`
  - `TimelineResponse`: `{ contract_number, components: Record<ComponentType, TimelineComponentWindow> }`

- `app/db/models/component_state.py`
  - SQLAlchemy model `ComponentState`
  - Columns: `id`, `contract_id (FK)`, `component_type (Enum)`, `start_date`, `start_event_created_at`, `end_date`, `end_event_created_at`
  - Constraint: unique `(contract_id, component_type)`

- `app/db/crud/component_state.py`
  - `get_component_state(db, contract_id, component_type)`
  - `upsert_component_state(db, *, contract_id, component_type, ...)`
  - Note: CRUD is rule-agnostic; domain rules will be enforced in P1 services.

## Updated Files
- `app/dto/contract.py`
  - Added validator for `components` to ensure each entry is within `ComponentType` (accepts strings or enum values; normalizes to strings).

- `app/db/models/contract.py`
  - Confirmed uniqueness on `contract_number` via `unique=True` and kept it indexed.

---

## Design Notes
- Enums centralize domain constraints and enrich OpenAPI docs.
- `ComponentState` is the single source of truth for component lifecycle (start/end) derived from events; overwrite semantics will compare `created_at` timestamps in P1.
- We keep `Contract.components` as a JSON array for flexibility but validate values strictly at the API boundary.

## What’s Next (P1 Preview)
- Implement `POST /event` with a rule engine to enforce ordering and lifecycle constraints:
  - Reject events for unknown contracts
  - Enforce created_at ordering for overwrite semantics
  - Reject end-before-start, start-after-end (restart), unsupported event types
  - Record state updates via `ComponentState`
- Implement `GET /{contract_number}/contract_timeline` by aggregating `ComponentState`.
- Add comprehensive tests for valid, invalid, and edge-case scenarios.

## Compatibility & Migration
- Tables are created automatically on startup via the existing `create_db_and_tables()` in `app/main.py` → `app/db/session.py`.
- Introducing `ComponentState` is additive; no breaking change to `Contract` schema beyond uniqueness which was already set in the model.


