"""Explanation ORM entity — stores the fact/interpretation distinction for a generated
explanation, looked up by its own ``explanation_id`` (Story 9389398)."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Boolean, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Explanation(Base):
    __tablename__ = "explanation"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    explanation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
    )
    facts: Mapped[list[str]] = mapped_column(
        ARRAY(Text()),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )
    interpretations: Mapped[list[str]] = mapped_column(
        ARRAY(Text()),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )
    unavailable_info: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
