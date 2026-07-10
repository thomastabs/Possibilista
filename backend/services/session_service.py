"""Student session validation and persistence logic."""

from __future__ import annotations

import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.student_interest import StudentInterest
from backend.models.student_session import StudentSession

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
