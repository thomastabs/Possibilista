"""Profiling endpoints for student interest and strengths/weakness collection."""

from __future__ import annotations

import logging
from typing import Any, Iterable

from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.student_interest import StudentInterest
from backend.models.student_session import StudentSession
from backend.models.student_strength_weakness import StudentStrengthWeakness

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


def _normalize_text_list_item(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Each item in '{field_name}' must be a string.",
        )

    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{field_name}' cannot contain empty values.",
        )
    return cleaned


def _parse_strengths_weaknesses_payload(payload: Any) -> tuple[list[str], list[str], bool]:
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be a JSON object.",
        )

    required_fields = {"strengths", "weaknesses", "partial"}
    if not required_fields.issubset(payload):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fields 'strengths', 'weaknesses', and 'partial' are required.",
        )

    strengths = payload["strengths"]
    weaknesses = payload["weaknesses"]
    partial = payload["partial"]

    if not isinstance(partial, bool):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'partial' must be a boolean.",
        )
    if not isinstance(strengths, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'strengths' must be a list of strings.",
        )
    if not isinstance(weaknesses, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'weaknesses' must be a list of strings.",
        )

    cleaned_strengths = [_normalize_text_list_item(item, "strengths") for item in strengths]
    cleaned_weaknesses = [_normalize_text_list_item(item, "weaknesses") for item in weaknesses]

    if not partial and not cleaned_strengths and not cleaned_weaknesses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one strength or weakness is required when partial is false.",
        )

    return cleaned_strengths, cleaned_weaknesses, partial


async def recommend_compatible_secondary_tracks(
    strengths: list[str],
    weaknesses: list[str],
    partial: bool,
) -> list[str]:
    logger.info(
        "Recommendation hook invoked for academic strengths/weaknesses.",
        extra={
            "strengths_count": len(strengths),
            "weaknesses_count": len(weaknesses),
            "partial": partial,
        },
    )
    return []


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


async def upsert_student_strength_weakness(
    db: AsyncSession,
    student_session: StudentSession,
    strengths: list[str],
    weaknesses: list[str],
    partial: bool,
) -> StudentStrengthWeakness:
    if student_session.school_year != 9:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only 9.º ano students can submit academic strengths and weaknesses.",
        )

    try:
        result = await db.execute(
            select(StudentStrengthWeakness).where(
                StudentStrengthWeakness.session_id == student_session.id,
            )
        )
        record = result.scalar_one_or_none()

        if record is None:
            record = StudentStrengthWeakness(
                session_id=student_session.id,
                strengths=strengths,
                weaknesses=weaknesses,
                partial=partial,
            )
            db.add(record)
        else:
            record.strengths = strengths
            record.weaknesses = weaknesses
            record.partial = partial

        await db.commit()
        return record
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Failed to persist student strengths and weaknesses.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save academic strengths and weaknesses.",
        ) from exc


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


@router.post("/strengths-weaknesses")
async def submit_student_strengths_weaknesses(
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

    strengths, weaknesses, partial = _parse_strengths_weaknesses_payload(payload)
    logger.info(
        "Received academic strengths/weaknesses submission.",
        extra={
            "session_id": str(student_session.id),
            "partial": partial,
            "strengths_count": len(strengths),
            "weaknesses_count": len(weaknesses),
        },
    )

    record = await upsert_student_strength_weakness(db, student_session, strengths, weaknesses, partial)
    recommendations = await recommend_compatible_secondary_tracks(
        record.strengths,
        record.weaknesses,
        record.partial,
    )

    logger.info(
        "Recommendation hook completed for academic strengths/weaknesses.",
        extra={
            "session_id": str(student_session.id),
            "recommendations_count": len(recommendations),
        },
    )

    if partial:
        message = "Academic strengths and weaknesses saved with partial input."
    else:
        message = "Academic strengths and weaknesses saved successfully."

    return {"status": "success", "message": message}
