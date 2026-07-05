"""Secondary track ORM entities."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class SecondaryTrack(Base):
    __tablename__ = "secondary_track"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    disciplines: Mapped[list["SecondaryTrackDiscipline"]] = relationship(
        back_populates="track",
        cascade="all, delete-orphan",
    )


class SecondaryTrackDiscipline(Base):
    __tablename__ = "secondary_track_discipline"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    track_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("secondary_track.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    discipline_name: Mapped[str] = mapped_column(String(255), nullable=False)

    track: Mapped[SecondaryTrack] = relationship(back_populates="disciplines")

