"""Profiling endpoints for student interest collection."""

from __future__ import annotations

import logging
from typing import Any, Iterable

from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.student_interest import StudentInterest
from backend.models.student_session import StudentSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/profiling", tags=["profiling"])
bearer_scheme = HTTPBearer(auto_error=True)


async def get_db_session(request: Request) -> AsyncSession:
    db = getattr(request.state, "db", None) or getattr(request.state, "db_session", None)
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database session is not available.",
        )
    return db


async def get_current_student_session(request: Request) -> StudentSession:
    session = (
        getattr(request.state, "student_session", None)
        or getattr(request.state, "current_session", None)
        or getattr(request.state, "session", None)
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )
    return session


def _normalize_interest(value: Any) -> str:
    if not isinstance(value, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Each interest must be a string.",
        )

    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interests cannot contain empty values.",
        )
    return cleaned


def _parse_interest_payload(payload: Any) -> tuple[list[str], bool]:
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be a JSON object.",
        )

    if "interests" not in payload or "skipped" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fields 'interests' and 'skipped' are required.",
        )

    interests = payload["interests"]
    skipped = payload["skipped"]

    if not isinstance(skipped, bool):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'skipped' must be a boolean.",
        )

    if not isinstance(interests, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'interests' must be a list of strings.",
        )

    cleaned_interests = [_normalize_interest(interest) for interest in interests]
    if not skipped and not cleaned_interests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one interest is required when skipped is false.",
        )

    return cleaned_interests, skipped


async def record_student_interests(
    db: AsyncSession,
    student_session: StudentSession,
    interests: Iterable[str],
    skipped: bool,
) -> int:
    if student_session.school_year != 9:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only 9.º ano students can submit interest preferences.",
        )

    records: list[StudentInterest] = []
    if skipped:
        records.append(
            StudentInterest(
                session_id=student_session.id,
                interest=None,
                skipped=True,
            )
        )
    else:
        for interest in interests:
            records.append(
                StudentInterest(
                    session_id=student_session.id,
                    interest=interest,
                    skipped=False,
                )
            )

    try:
        db.add_all(records)
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Failed to persist student interests.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save student interests.",
        ) from exc

    return len(records)


@router.post("/interests")
async def submit_student_interests(
    request: Request,
    _credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
    student_session: StudentSession = Depends(get_current_student_session),
) -> dict[str, str]:
    try:
        payload = await request.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be valid JSON.",
        ) from exc

    interests, skipped = _parse_interest_payload(payload)
    saved_count = await record_student_interests(db, student_session, interests, skipped)

    if skipped:
        message = "Interest questions were skipped and the skip was recorded."
    else:
        message = f"Recorded {saved_count} student interest preference(s)."

    return {"status": "success", "message": message}
