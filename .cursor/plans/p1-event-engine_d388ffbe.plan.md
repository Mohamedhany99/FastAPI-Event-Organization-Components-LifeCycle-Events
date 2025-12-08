---
name: p1-event-engine
overview: Implement event ingestion and contract timeline endpoints with full rule enforcement over component lifecycles, using ComponentState as source of truth. Add comprehensive tests.
todos:
  - id: add-event-router
    content: Create app/api/routers/event.py with POST /event endpoint
    status: completed
  - id: implement-event-service
    content: Add app/api/services/event_services.py with process_event logic and rules
    status: completed
  - id: add-timeline-service
    content: Add app/api/services/timeline_services.py to build timeline response
    status: completed
  - id: wire-event-router
    content: Include event router in app/main.py
    status: completed
  - id: add-list-component-states
    content: Add list_component_states in app/db/crud/component_state.py
    status: completed
  - id: add-event-tests
    content: Create tests/api/test_event.py covering valid, invalid, overwrite scenarios
    status: completed
  - id: add-timeline-tests
    content: Create tests/api/test_timeline.py covering aggregation and README scenario
    status: completed
---

# P1 — Event Engine and Endpoints

## Scope

Implement the event processing engine and expose endpoints to ingest events and retrieve a contract’s component timelines. Enforce domain rules using `ComponentState` as the source of truth.

## Endpoints

- Add: [app/api/routers/event.py](app/api/routers/event.py)
  - `POST /event`
    - Input: `EventPayload` ([app/dto/event.py](app/dto/event.py))
    - Output: `EventResponse` (accepted|rejected + message)
- Add/Update: [app/api/routers/contract.py](app/api/routers/contract.py)
  - `GET /{contract_number}/contract_timeline`
    - Output: `TimelineResponse` ([app/dto/timeline.py](app/dto/timeline.py))
- Update: [app/main.py](app/main.py)
  - Include the new `event` router

## Services

- Add: [app/api/services/event_services.py](app/api/services/event_services.py)
  - `process_event(db: AsyncSession, payload: EventPayload) -> EventResponse`
    - Parse `payload.type` → `(component, action)` via `resolve_component_action`
    - Load contract by `contract_number`, reject if not found
    - Optionally validate component is present in `contract.components`
    - Load or create `ComponentState` by `(contract_id, component_type)`
    - Enforce rules:
      - Ordering by `created_at` for overwrite semantics
      - Start-after-end (restart) → reject
      - End-without-start → reject
      - Component cannot end before it starts (validate dates)
      - If start/end exists and incoming event is older than the recorded event (by `created_at`), ignore/keep existing (respond accepted with no change or rejected with message; choose “rejected” to be explicit)
    - Persist via `upsert_component_state`
    - Return standardized `EventResponse`
- Add: [app/api/services/timeline_services.py](app/api/services/timeline_services.py)
  - `get_contract_timeline(db: AsyncSession, contract_number: str) -> TimelineResponse`
    - Load contract, 404 if not found
    - Query states for that contract and build `components` map of `{component: {start, end}}`

## CRUD/Queries

- Add: lightweight query to list `ComponentState` for a contract
  - File: [app/db/crud/component_state.py](app/db/crud/component_state.py)
  - Function: `list_component_states(db, contract_id) -> list[ComponentState]`

## Error Model

- Keep `EventResponse` for success/failure of `POST /event`
- For timeline and contract not found, continue using FastAPI HTTPException with JSON body matching README examples

## Tests

- Add: [tests/api/test_event.py](tests/api/test_event.py)
  - Accepts valid start/end for each component
  - Rejects: unknown contract, unsupported event type, end-before-start (date), start-after-end (restart), older duplicate events (created_at older)
  - Overwrite semantics: newer start overwrites start; newer end overwrites end
- Add: [tests/api/test_timeline.py](tests/api/test_timeline.py)
  - Asserts correct aggregation from `ComponentState` after sequences of events
  - Use README example sequence as a scenario

## Small Reference (signatures)

```python
models# app/api/routers/event.py
@router.post("/event", response_model=EventResponse)
async def post_event(payload: EventPayload, db: AsyncSession = Depends(get_async_session)):
    return await process_event(db, payload)

# app/api/routers/contract.py
@router.get("/{contract_number}/contract_timeline", response_model=TimelineResponse)
async def get_timeline(contract_number: str, db: AsyncSession = Depends(get_async_session)):
    return await get_contract_timeline(db, contract_number)
```

## Out-of-Scope (deferred)

- Event audit table (append-only). Consider in P2/P3.
- Batch ingestion; we only support single-event ingestion in P1.