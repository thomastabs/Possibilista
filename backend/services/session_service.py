"""Student session validation and persistence logic."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chat_message import ChatMessage
from backend.models.session_secondary_track_memory import SessionSecondaryTrackMemory
from backend.models.student_interest import StudentInterest
from backend.models.student_motivation import StudentMotivation
from backend.models.student_session import StudentSession
from backend.models.student_strength_weakness import StudentStrengthWeakness

logger = logging.getLogger(__name__)

MIN_SCHOOL_YEAR = 9
MAX_SCHOOL_YEAR = 12

SCHOOL_YEAR_INVALID_MESSAGE = (
    f"Please provide a valid school year between {MIN_SCHOOL_YEAR} and {MAX_SCHOOL_YEAR}."
)


def validate_school_year(school_year: int) -> tuple[bool, str]:
    """Check whether school_year falls within the allowed 9.º-12.º range."""
    if MIN_SCHOOL_YEAR <= school_year <= MAX_SCHOOL_YEAR:
        return True, ""
    return False, SCHOOL_YEAR_INVALID_MESSAGE


async def record_student_interests(
    db: AsyncSession,
    student_session: StudentSession,
    interests: list[str],
    skipped: bool,
) -> int:
    """Normalize and persist StudentInterest rows for a session.

    Returns the number of interest records saved (0 for a skipped-only record).
    """
    normalized_interests = [interest.strip() for interest in interests if interest.strip()]

    if skipped or not normalized_interests:
        records = [
            StudentInterest(session_id=student_session.id, interest=None, skipped=True)
        ]
        saved_count = 0
    else:
        records = [
            StudentInterest(session_id=student_session.id, interest=interest, skipped=False)
            for interest in normalized_interests
        ]
        saved_count = len(records)

    try:
        db.add_all(records)
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception(
            "Failed to persist student interests.",
            extra={"session_id": str(student_session.id)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the student's interests.",
        ) from exc

    logger.info(
        "Persisted student interests.",
        extra={
            "session_id": str(student_session.id),
            "skipped": skipped,
            "saved_count": saved_count,
        },
    )
    return saved_count


async def update_secondary_track_memory(
    db: AsyncSession, session_id: str, track_id: str
) -> SessionSecondaryTrackMemory:
    """Upsert the SessionSecondaryTrackMemory row for a session with the explored track."""
    try:
        parsed_session_id = UUID(session_id)
        parsed_track_id = UUID(track_id)
    except (ValueError, AttributeError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id and track_id must be valid UUIDs.",
        ) from exc

    result = await db.execute(
        select(StudentSession).where(StudentSession.id == parsed_session_id)
    )
    student_session = result.scalar_one_or_none()
    if student_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or unauthorized.",
        )

    result = await db.execute(
        select(SessionSecondaryTrackMemory).where(
            SessionSecondaryTrackMemory.session_id == parsed_session_id
        )
    )
    memory = result.scalars().one_or_none()

    if memory is None:
        memory = SessionSecondaryTrackMemory(
            session_id=parsed_session_id, stored_track_id=parsed_track_id
        )
        db.add(memory)
    else:
        memory.stored_track_id = parsed_track_id

    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception(
            "Failed to persist secondary track memory.",
            extra={"session_id": session_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the explored secondary track.",
        ) from exc

    logger.info(
        "Updated secondary track memory.",
        extra={"session_id": session_id, "stored_track_id": track_id},
    )
    return memory


async def clear_student_session_data(db: AsyncSession, session_id: str) -> StudentSession:
    """Reset a StudentSession's fields and delete all data linked to it.

    Clears student_name, age, and school_year, and deletes every StudentInterest,
    StudentMotivation, StudentStrengthWeakness, ChatMessage, and
    SessionSecondaryTrackMemory row for the session.
    """
    try:
        parsed_session_id = UUID(session_id)
    except (ValueError, AttributeError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id must be a valid UUID.",
        ) from exc

    result = await db.execute(
        select(StudentSession).where(StudentSession.id == parsed_session_id)
    )
    student_session = result.scalar_one_or_none()
    if student_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or unauthorized.",
        )

    student_session.student_name = None
    student_session.age = None
    student_session.school_year = None

    try:
        await db.execute(
            delete(StudentInterest).where(StudentInterest.session_id == parsed_session_id)
        )
        await db.execute(
            delete(StudentMotivation).where(StudentMotivation.session_id == parsed_session_id)
        )
        await db.execute(
            delete(StudentStrengthWeakness).where(
                StudentStrengthWeakness.session_id == parsed_session_id
            )
        )
        await db.execute(delete(ChatMessage).where(ChatMessage.session_id == parsed_session_id))
        await db.execute(
            delete(SessionSecondaryTrackMemory).where(
                SessionSecondaryTrackMemory.session_id == parsed_session_id
            )
        )
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception(
            "Failed to clear student session data.", extra={"session_id": session_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to clear the student's session data.",
        ) from exc

    logger.info("Cleared student session data.", extra={"session_id": session_id})
    return student_session
