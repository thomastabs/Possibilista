"""Chat message ORM entity.

Stores a single conversational turn, including the structured facts /
interpretations breakdown of the answer (Story 9389364) and the dialogue
context fields used to link turns and detect topic changes across a
multi-turn conversation (Story 9389366): ``previous_message_id`` points to
the prior turn in the same session, and ``context_tokens`` records the
topic identity (matched official-document titles) of this turn so the next
turn can decide whether to retain or reset context.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .student_session import StudentSession


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("student_session.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
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
    insufficient_info: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    requires_confirmation: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    previous_message_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("chat_message.id", ondelete="SET NULL"),
        nullable=True,
    )
    context_tokens: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text()),
        nullable=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )

    session: Mapped[StudentSession] = relationship(back_populates="chat_messages")
