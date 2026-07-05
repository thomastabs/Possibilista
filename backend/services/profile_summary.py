"""Profile summary generation service."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.student_interest import StudentInterest
from backend.models.student_motivation import StudentMotivation
from backend.models.student_strength_weakness import StudentStrengthWeakness

logger = logging.getLogger(__name__)


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _append_suggestion(suggestions: list[str], suggestion: str) -> None:
    if suggestion not in suggestions:
        suggestions.append(suggestion)


async def fetch_student_interests(db: AsyncSession, session_id: str) -> list[StudentInterest]:
    try:
        result = await db.execute(
            select(StudentInterest).where(
                StudentInterest.session_id == session_id,
                StudentInterest.skipped.is_(False),
            )
        )
        return [item for item in result.scalars().all() if not getattr(item, "skipped", False)]
    except SQLAlchemyError:
        logger.exception("Failed to load student interests for profile summary.")
        return []


async def fetch_student_motivation(db: AsyncSession, session_id: str) -> StudentMotivation | None:
    try:
        result = await db.execute(
            select(StudentMotivation).where(StudentMotivation.session_id == session_id)
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError:
        logger.exception("Failed to load student motivation for profile summary.")
        return None


async def fetch_student_strengths_weaknesses(
    db: AsyncSession, session_id: str
) -> StudentStrengthWeakness | None:
    try:
        result = await db.execute(
            select(StudentStrengthWeakness).where(StudentStrengthWeakness.session_id == session_id)
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError:
        logger.exception("Failed to load student strengths/weaknesses for profile summary.")
        return None


async def generate_profile_summary(db: AsyncSession, session_id: str) -> dict[str, Any]:
    """Aggregate student inputs into a summary plus completion suggestions."""

    interests = await fetch_student_interests(db, session_id)
    motivation = await fetch_student_motivation(db, session_id)
    strengths_record = await fetch_student_strengths_weaknesses(db, session_id)

    summary_parts: list[str] = []
    missing_fields: list[str] = []
    suggestions: list[str] = []

    interest_items = _dedupe_preserve_order(
        [item.interest or "" for item in interests if getattr(item, "interest", None)]
    )
    if interest_items:
        summary_parts.append(f"Interests captured: {', '.join(interest_items)}.")
    else:
        summary_parts.append("No interests have been recorded yet.")
        missing_fields.append("interests")
        _append_suggestion(
            suggestions,
            "Share a few subjects, activities, or topics you enjoy to refine guidance.",
        )

    if motivation is None:
        summary_parts.append("Motivation information is missing.")
        missing_fields.append("motivations")
        _append_suggestion(
            suggestions,
            "Describe what motivates your choices so the advice can be personalized.",
        )
    elif motivation.declined:
        summary_parts.append("Motivation questions were declined.")
        missing_fields.append("motivations")
        _append_suggestion(
            suggestions,
            "You can add motivations later if you want more personalized guidance.",
        )
    elif motivation.motivations and motivation.motivations.strip():
        summary_parts.append(f"Motivations captured: {motivation.motivations.strip()}.")
    else:
        summary_parts.append("Motivation information is incomplete.")
        missing_fields.append("motivations")
        _append_suggestion(
            suggestions,
            "Provide a short motivation statement to improve the profile summary.",
        )

    if strengths_record is None:
        summary_parts.append("Academic strengths and weaknesses are missing.")
        missing_fields.append("academic_strengths_weaknesses")
        _append_suggestion(
            suggestions,
            "List the disciplines you feel strong in and the ones you want to improve.",
        )
    else:
        strengths = _dedupe_preserve_order([item for item in strengths_record.strengths if item])
        weaknesses = _dedupe_preserve_order([item for item in strengths_record.weaknesses if item])
        strengths_text = ", ".join(strengths) if strengths else "none provided"
        weaknesses_text = ", ".join(weaknesses) if weaknesses else "none provided"

        if strengths_record.partial:
            summary_parts.append(
                "Academic strengths and weaknesses were provided partially "
                f"(strengths: {strengths_text}; weaknesses: {weaknesses_text})."
            )
            missing_fields.append("academic_strengths_weaknesses")
            _append_suggestion(
                suggestions,
                "Add a few more strong and weak disciplines to improve track recommendations.",
            )
        else:
            summary_parts.append(
                f"Academic strengths: {strengths_text}. Academic weaknesses: {weaknesses_text}."
            )

    logger.info(
        "Generated profile summary.",
        extra={
            "session_id": session_id,
            "missing_fields_count": len(missing_fields),
            "suggestions_count": len(suggestions),
        },
    )

    return {
        "profile_summary": " ".join(summary_parts),
        "missing_fields": missing_fields,
        "suggestions": suggestions,
    }
