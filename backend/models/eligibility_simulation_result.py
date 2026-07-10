"""Eligibility simulation result ORM entity."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .secondary_track import SecondaryTrack


class EligibilitySimulationResult(Base):
    __tablename__ = "eligibility_simulation_result"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    secondary_track_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("secondary_track.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    eligible_courses: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    incomplete_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    track: Mapped[SecondaryTrack] = relationship(back_populates="eligibility_simulation_results")
