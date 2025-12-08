import uuid
from datetime import date, datetime, timezone

from sqlalchemy import DateTime, String, JSON, ForeignKey, UniqueConstraint, Date, Index
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.domain.enums import ComponentType, EventAction, EventType
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Index



def utc_now() -> datetime:
    """A workaround to use utc time, since datetime.utcnow is deprecated."""
    return datetime.now(timezone.utc)


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, index=True
    )
    contract_number: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    components: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

class ComponentState(Base):
    __tablename__ = "component_state"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, index=True
    )
    contract_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contract.id"), nullable=False, index=True
    )
    component_type: Mapped[ComponentType] = mapped_column(
        SAEnum(ComponentType, name="component_type"), nullable=False
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    start_event_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_event_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        UniqueConstraint("contract_id", "component_type", name="uq_contract_component"),
        Index("ix_component_state_contract_component", "contract_id", "component_type"),
    )


class Event(Base):
    __tablename__ = "event_audit"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, index=True
    )
    contract_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("contract.id"), nullable=True, index=True
    )
    raw_type: Mapped[EventType] = mapped_column(SAEnum(EventType, name="event_type"), nullable=False)
    component_type: Mapped[ComponentType | None] = mapped_column(SAEnum(ComponentType, name="component_type"), nullable=True)
    action: Mapped[EventAction | None] = mapped_column(SAEnum(EventAction, name="event_action"), nullable=True)
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    event_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    status: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("ix_event_audit_contract_created_at", "contract_id", "event_created_at"),
    )

