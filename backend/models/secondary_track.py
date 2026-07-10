"""Secondary track ORM entities."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
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
    exam_requirements: Mapped[list["SecondaryTrackExamRequirement"]] = relationship(
        back_populates="track",
        cascade="all, delete-orphan",
    )
    discipline_combination: Mapped["SecondaryTrackDisciplineCombination | None"] = relationship(
        back_populates="track",
        cascade="all, delete-orphan",
        uselist=False,
    )
    higher_ed_impact: Mapped["SecondaryTrackHigherEdImpact | None"] = relationship(
        back_populates="track",
        cascade="all, delete-orphan",
        uselist=False,
    )
    course_compatibilities: Mapped[list["HigherEdCourseCompatibility"]] = relationship(
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


class SecondaryTrackExamRequirement(Base):
    __tablename__ = "secondary_track_exam_requirement"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    track_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("secondary_track.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exam_name: Mapped[str] = mapped_column(String(255), nullable=False)
    timing: Mapped[str] = mapped_column(String(255), nullable=False)

    track: Mapped[SecondaryTrack] = relationship(back_populates="exam_requirements")


class SecondaryTrackDisciplineCombination(Base):
    __tablename__ = "secondary_track_discipline_combination"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    track_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("secondary_track.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    trienais: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    bienais: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    anuais: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    combinations: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    track: Mapped[SecondaryTrack] = relationship(back_populates="discipline_combination")


class SecondaryTrackHigherEdImpact(Base):
    __tablename__ = "secondary_track_higher_ed_impact"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    track_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("secondary_track.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    impact_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    track: Mapped[SecondaryTrack] = relationship(back_populates="higher_ed_impact")

