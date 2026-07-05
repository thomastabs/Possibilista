"""Profiling endpoints for student interest and strengths/weakness collection."""

from __future__ import annotations

import logging
from typing import Any, Iterable

from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.student_interest import StudentInterest
from backend.models.student_session import StudentSession
from backend.models.secondary_track import SecondaryTrack
from backend.models.student_motivation import StudentMotivation
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


def _parse_motivation_payload(payload: Any) -> tuple[str | None, bool]:
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be a JSON object.",
        )

    if "motivations" not in payload or "declined" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fields 'motivations' and 'declined' are required.",
        )

    motivations = payload["motivations"]
    declined = payload["declined"]

    if not isinstance(declined, bool):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'declined' must be a boolean.",
        )

    if declined:
        if motivations not in (None, "") and not isinstance(motivations, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field 'motivations' must be a string when provided.",
            )
        if isinstance(motivations, str) and motivations.strip() == "":
            motivations = None
        return None, True

    if not isinstance(motivations, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'motivations' must be a string.",
        )

    cleaned = motivations.strip()
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Motivations cannot be empty when declined is false.",
        )

    return cleaned, False


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
    db: AsyncSession,
    strengths: list[str],
    weaknesses: list[str],
    partial: bool,
) -> list[str]:
    normalized_strengths = {item.casefold() for item in strengths}
    normalized_weaknesses = {item.casefold() for item in weaknesses}

    logger.info(
        "Recommendation hook invoked for academic strengths/weaknesses.",
        extra={
            "strengths_count": len(strengths),
            "weaknesses_count": len(weaknesses),
            "partial": partial,
        },
    )

    if partial and not normalized_strengths and not normalized_weaknesses:
        logger.info(
            "Recommendation request needs clarification due to sparse partial input.",
            extra={"partial": partial},
        )
        return [
            "Clarification needed: please provide more detail about your strongest and weakest disciplines.",
        ]

    try:
        result = await db.execute(
            select(SecondaryTrack).options(selectinload(SecondaryTrack.disciplines))
        )
        tracks = result.scalars().unique().all()
    except SQLAlchemyError as exc:
        logger.exception("Failed to load secondary tracks for recommendation.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to evaluate compatible secondary tracks.",
        ) from exc

    scored_tracks: list[tuple[int, SecondaryTrack]] = []
    for track in tracks:
        track_terms = {track.name.casefold()}
        if track.description:
            track_terms.update(track.description.casefold().split())
        discipline_terms = {discipline.discipline_name.casefold() for discipline in track.disciplines}
        all_terms = track_terms | discipline_terms

        strength_matches = sum(1 for value in normalized_strengths if value in all_terms)
        weakness_matches = sum(1 for value in normalized_weaknesses if value in all_terms)
        score = (strength_matches * 3) - (weakness_matches * 2)

        logger.info(
            "Scored secondary track candidate.",
            extra={
                "track_id": str(track.id),
                "track_name": track.name,
                "strength_matches": strength_matches,
                "weakness_matches": weakness_matches,
                "score": score,
            },
        )

        if score > 0:
            scored_tracks.append((score, track))

    scored_tracks.sort(key=lambda item: (-item[0], item[1].name.lower()))
    recommended_ids = [str(track.id) for _, track in scored_tracks[:3]]

    if recommended_ids:
        if partial:
            logger.info(
                "Partial input produced limited secondary-track recommendations.",
                extra={"recommended_count": len(recommended_ids)},
            )
        return recommended_ids

    logger.info(
        "No confident secondary-track recommendation could be made.",
        extra={"partial": partial},
    )
    return [
        "Clarification needed: the current strengths and weaknesses do not confidently match a secondary track.",
    ]


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


async def upsert_student_motivation(
    db: AsyncSession,
    student_session: StudentSession,
    motivations: str | None,
    declined: bool,
) -> StudentMotivation:
    if student_session.school_year != 9:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only 9.º ano students can submit motivations.",
        )

    try:
        result = await db.execute(
            select(StudentMotivation).where(StudentMotivation.session_id == student_session.id)
        )
        record = result.scalar_one_or_none()

        if record is None:
            record = StudentMotivation(
                session_id=student_session.id,
                motivations=motivations,
                declined=declined,
            )
            db.add(record)
        else:
            record.motivations = motivations
            record.declined = declined

        await db.commit()
        return record
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Failed to persist student motivations.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save motivations.",
        ) from exc


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


async def get_student_profile_summary(
    db: AsyncSession,
    student_session: StudentSession,
) -> dict[str, Any]:
    try:
        interests_result = await db.execute(
            select(StudentInterest).where(StudentInterest.session_id == student_session.id)
        )
        interests = interests_result.scalars().all()

        strengths_result = await db.execute(
            select(StudentStrengthWeakness).where(
                StudentStrengthWeakness.session_id == student_session.id,
            )
        )
        strengths_record = strengths_result.scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.exception("Failed to load profile summary data.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load profile summary.",
        ) from exc

    summary_parts: list[str] = []
    missing_fields: list[str] = []

    if interests:
        selected_interests = [item.interest for item in interests if item.interest]
        summary_parts.append(f"Interests captured: {', '.join(selected_interests)}.")
    else:
        missing_fields.append("interests")

    if strengths_record is not None:
        summary_parts.append(
            "Academic strengths and weaknesses recorded "
            f"({len(strengths_record.strengths)} strengths, {len(strengths_record.weaknesses)} weaknesses)."
        )
    else:
        missing_fields.append("academic_strengths_weaknesses")

    if not summary_parts:
        summary_parts.append("Profile summary is not yet complete.")

    recommendations: list[str] = []
    if strengths_record is not None:
        recommendations = await recommend_compatible_secondary_tracks(
            db,
            strengths_record.strengths,
            strengths_record.weaknesses,
            strengths_record.partial,
        )
    else:
        recommendations = [
            "Clarification needed: add academic strengths and weaknesses to receive secondary-track recommendations.",
        ]

    logger.info(
        "Profile summary loaded.",
        extra={
            "session_id": str(student_session.id),
            "missing_fields_count": len(missing_fields),
            "recommendations_count": len(recommendations),
        },
    )

    return {
        "status": "success",
        "profile_summary": " ".join(summary_parts),
        "missing_fields": missing_fields,
        "recommendations": recommendations,
    }


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
        db,
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

    if recommendations and recommendations[0].startswith("Clarification needed:"):
        message = (
            "Academic strengths and weaknesses saved, but more detail is needed before recommending tracks. "
            f"{recommendations[0]}"
        )
    elif partial:
        message = (
            "Academic strengths and weaknesses saved with partial input. "
            f"Limited recommendations: {', '.join(recommendations)}"
        )
    else:
        message = f"Academic strengths and weaknesses saved successfully. Recommended tracks: {', '.join(recommendations)}"

    return {"status": "success", "message": message}


@router.post("/motivations")
async def submit_student_motivations(
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

    motivations, declined = _parse_motivation_payload(payload)
    logger.info(
        "Received motivations submission.",
        extra={
            "session_id": str(student_session.id),
            "declined": declined,
            "motivations_present": motivations is not None,
        },
    )

    await upsert_student_motivation(db, student_session, motivations, declined)

    if declined:
        message = "Motivations declined and recorded."
    else:
        message = "Motivations saved successfully."

    return {"status": "success", "message": message}


@router.get("/summary")
async def get_profile_summary_endpoint(
    _credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
    student_session: StudentSession = Depends(get_current_student_session),
) -> dict[str, Any]:
    return await get_student_profile_summary(db, student_session)
