import uuid
from datetime import date, datetime, timezone

from sqlalchemy import DateTime, String, JSON, ForeignKey, UniqueConstraint,Date
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.domain.enums import ComponentType



def utc_now() -> datetime:
    """A workaround to use utc time, since datetime.utcnow is deprecated."""
    return datetime.now(timezone.utc)


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, index=True
    )
    contract_number: Mapped[str] = mapped_column(String, nullable=False, unique=True)
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
    )


