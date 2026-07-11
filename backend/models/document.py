"""Document ORM entity — indexed official documents backing source-grounded retrieval.

``embedding`` is a real ``pgvector`` column; only its value generation is currently a
deterministic stub (see ``DETERMINISTIC_STUBS.md``) rather than a live embedding call.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

EMBEDDING_DIMENSIONS = 8


class Document(Base):
    __tablename__ = "document"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(
        String(512), nullable=False, unique=True, index=True
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    version_label: Mapped[str] = mapped_column(String(100), nullable=False)
    indexed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    indexing_errors: Mapped[list[str]] = mapped_column(
        ARRAY(Text()),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS), nullable=True
    )
