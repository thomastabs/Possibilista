"""Chat message endpoint — conversational answers with facts/interpretations."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.profiling import get_db_session
from backend.models.chat_message import ChatMessage
from backend.models.student_session import StudentSession
from backend.services.chat_service import build_chat_response_for_message, get_last_chat_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
bearer_scheme = HTTPBearer(auto_error=True)


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = Field(min_length=1)


class ChatMessageResponse(BaseModel):
    answer: str
    facts: list[str]
    interpretations: list[str]
    insufficient_info: bool = Field(
        description="True when the question has no basis in official document sources.",
    )
    requires_confirmation: bool = Field(
        description="True when the question covers a special case or exception requiring "
        "human or institutional confirmation.",
    )
    is_fact: bool = Field(
        description="True when the answer includes at least one documented fact grounded "
        "in official sources.",
    )
    is_interpretation: bool = Field(
        description="True when the answer includes interpretative or uncertain content.",
    )
    documents: list[dict] = Field(
        description="Official documents (title, content, source_url) grounding the facts in "
        "this answer, freshly retrieved per request. Empty when the answer is not grounded.",
    )
    confirmation_advice: str | None = Field(
        default=None,
        description="Advisory message prompting the student to confirm with a human or "
        "institution, present whenever requires_confirmation is true.",
    )
    session_id: str


async def resolve_student_session(db: AsyncSession, session_id: str) -> StudentSession:
    try:
        session_uuid = UUID(session_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or unauthorized.",
        ) from exc

    result = await db.execute(select(StudentSession).where(StudentSession.id == session_uuid))
    student_session = result.scalar_one_or_none()
    if student_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or unauthorized.",
        )
    return student_session


async def persist_chat_message(
    db: AsyncSession,
    student_session: StudentSession,
    message: str,
    response: dict[str, Any],
) -> ChatMessage:
    previous_message_id = response.get("previous_message_id")
    record = ChatMessage(
        session_id=student_session.id,
        message=message,
        answer=response["answer"],
        facts=response["facts"],
        interpretations=response["interpretations"],
        insufficient_info=response["insufficient_info"],
        requires_confirmation=response["requires_confirmation"],
        is_fact=response["is_fact"],
        is_interpretation=response["is_interpretation"],
        previous_message_id=UUID(previous_message_id) if previous_message_id else None,
        context_tokens=response.get("context_tokens"),
    )

    try:
        db.add(record)
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Failed to persist chat message.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save chat message.",
        ) from exc

    return record


@router.post("/message", response_model=ChatMessageResponse)
async def post_chat_message(
    payload: ChatMessageRequest,
    _credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> ChatMessageResponse:
    student_session = await resolve_student_session(db, payload.session_id)

    logger.info(
        "Processing chat message request.",
        extra={"session_id": str(student_session.id)},
    )

    previous_message = await get_last_chat_message(db, str(student_session.id))

    try:
        response = build_chat_response_for_message(
            payload.message, str(student_session.id), previous_message
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    await persist_chat_message(db, student_session, payload.message, response)

    logger.info(
        "Chat message response prepared.",
        extra={
            "session_id": str(student_session.id),
            "facts_count": len(response["facts"]),
            "interpretations_count": len(response["interpretations"]),
            "insufficient_info": response["insufficient_info"],
            "requires_confirmation": response["requires_confirmation"],
            "is_fact": response["is_fact"],
            "is_interpretation": response["is_interpretation"],
            "documents_count": len(response["documents"]),
            "confirmation_advice_given": response["confirmation_advice"] is not None,
        },
    )

    return ChatMessageResponse(**response)
