import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


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
