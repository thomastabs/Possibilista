"""Session secondary track memory ORM entity."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .student_session import StudentSession


class SessionSecondaryTrackMemory(Base):
    __tablename__ = "session_secondary_track_memory"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("student_session.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    stored_track_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("secondary_track.id", ondelete="CASCADE"),
        nullable=False,
    )

    session: Mapped[StudentSession] = relationship(back_populates="secondary_track_memory")
