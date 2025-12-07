---
name: p0-core-domain
overview: Introduce domain enums, DTOs, and DB constraints needed to enforce component lifecycle rules and prepare for events/timelines. No code execution—just design and file placement to implement next.
todos:
  - id: add-enums
    content: Create app/domain/enums.py with ComponentType, EventAction, EventType mapping
    status: completed
  - id: add-event-dtos
    content: Add app/dto/event.py with EventPayload and EventResponse models
    status: completed
  - id: add-timeline-dtos
    content: Add app/dto/timeline.py with timeline response models
    status: completed
  - id: validate-contract-components
    content: Validate ContractPayload.components against ComponentType enum
    status: completed
  - id: unique-contract-number
    content: Add unique index/constraint to contract_number in contract model
    status: completed
  - id: add-component-state-model
    content: Create app/db/models/component_state.py with unique (contract_id, component_type)
    status: completed
  - id: component-state-crud
    content: Add app/db/crud/component_state.py with get/upsert helpers
    status: completed
---

# P0 — Core Domain and Constraints

## Scope

Define core domain types, DTOs, and persistence constraints required to enforce component lifecycle rules. Prepare the codebase for implementing the event engine and timeline endpoint in P1.

## Files to Add/Update

- Add: [app/domain/enums.py](app/domain/enums.py)
  - `ComponentType` enum: energy_supply, battery_optimization, heatpump_optimization
  - `EventAction` enum: start, end
  - `EventType` enum and mapping → `(component_type, action)`
- Add: [app/dto/event.py](app/dto/event.py)
  - `EventPayload`: `type`, `contract_number`, `date` (date), `created_at` (datetime)
  - `EventResponse`: `status` (accepted|rejected), `message`
- Add: [app/dto/timeline.py](app/dto/timeline.py)
  - `TimelineComponentWindow`: `start: date | None`, `end: date | None`
  - `TimelineResponse`: `contract_number`, `components: dict[ComponentType, TimelineComponentWindow]`
- Update: [app/dto/contract.py](app/dto/contract.py)
  - Validate `components ⊆ ComponentType` (either accept enum values directly or coerce strings → enum with a validator)
- Update: [app/db/models/contract.py](app/db/models/contract.py)
  - Add `Unique` constraint on `contract_number` and explicit index
- Add: [app/db/models/component_state.py](app/db/models/component_state.py)
  - SQLAlchemy model `ComponentState` with unique `(contract_id, component_type)`
  - Fields: `id (UUID PK)`, `contract_id (FK→contract.id)`, `component_type (Enum)`, `start_date (date)`, `start_event_created_at (datetime)`, `end_date (date|null)`, `end_event_created_at (datetime|null)`
- Add: [app/db/crud/component_state.py](app/db/crud/component_state.py)
  - Basic get/upsert helpers by `(contract_id, component_type)`

## Key Design Notes

- Enums centralize constraints and power OpenAPI schemas.
- `contract_number` must be globally unique to avoid ambiguous routing and event attribution.
- `ComponentState` is the single source of truth for current start/end per component; overwrite semantics will compare incoming `created_at` in P1.
- Keep contract `components` as JSON array in DB but validate values at API layer.

## Small Reference (concise schema sketch)

```python
# app/db/models/component_state.py
class ComponentState(Base):
    __tablename__ = "component_state"
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id = mapped_column(ForeignKey("contract.id"), index=True, nullable=False)
    component_type = mapped_column(SAEnum(ComponentType), nullable=False)
    start_date = mapped_column(Date, nullable=True)
    start_event_created_at = mapped_column(DateTime(timezone=True), nullable=True)
    end_date = mapped_column(Date, nullable=True)
    end_event_created_at = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (UniqueConstraint("contract_id", "component_type"),)
```

## Out-of-Scope (deferred to P1/P2)

- Event rule engine logic and endpoints (POST /event, GET /{contract_number}/contract_timeline)
- Comprehensive tests and error payload standardization