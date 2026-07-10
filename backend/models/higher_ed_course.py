"""Higher education course ORM entity."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class HigherEdCourse(Base):
    __tablename__ = "higher_ed_course"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    compatibilities: Mapped[list["HigherEdCourseCompatibility"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )
    entrance_exams: Mapped[list["HigherEdCourseEntranceExam"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )
