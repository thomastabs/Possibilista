"""Family-focused exploration path explanation service."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.profile_summary import (
    fetch_student_interests,
    fetch_student_motivation,
    fetch_student_strengths_weaknesses,
)

logger = logging.getLogger(__name__)

NO_INTERESTS_MESSAGE = "No interests have been recorded for this student yet."
NO_MOTIVATIONS_MESSAGE = "No motivation information has been recorded for this student yet."
NO_ACADEMIC_AREAS_MESSAGE = (
    "No academic strengths or weaknesses have been recorded for this student yet."
)
NO_DATA_MESSAGE = "This student has not started exploring yet."


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


async def get_exploration_path_explanation(db: AsyncSession, student_session_id: str) -> dict[str, Any]:
    """Aggregate a student's interests, motivations, and academic areas into plain language.

    Reuses the fetch helpers from ``profile_summary.py`` so both explanation surfaces stay in
    sync with the same underlying data. ``no_data`` is only true when all three categories are
    empty (Story 9389396); a category with no data on its own falls back to its own neutral
    message so the family view still reads coherently.
    """

    interests = await fetch_student_interests(db, student_session_id)
    motivation = await fetch_student_motivation(db, student_session_id)
    strengths_record = await fetch_student_strengths_weaknesses(db, student_session_id)

    interest_items = _dedupe_preserve_order(
        [item.interest or "" for item in interests if getattr(item, "interest", None)]
    )
    has_interests = bool(interest_items)
    interests_explanation = (
        f"The student is interested in: {', '.join(interest_items)}."
        if has_interests
        else NO_INTERESTS_MESSAGE
    )

    has_motivation = bool(
        motivation is not None and not motivation.declined and motivation.motivations
        and motivation.motivations.strip()
    )
    motivations_explanation = (
        f"The student is motivated by: {motivation.motivations.strip()}."
        if has_motivation
        else NO_MOTIVATIONS_MESSAGE
    )

    strengths: list[str] = []
    weaknesses: list[str] = []
    if strengths_record is not None:
        strengths = _dedupe_preserve_order([item for item in strengths_record.strengths if item])
        weaknesses = _dedupe_preserve_order([item for item in strengths_record.weaknesses if item])
    has_academic_areas = bool(strengths or weaknesses)

    if has_academic_areas:
        parts = []
        if strengths:
            parts.append(f"strong in {', '.join(strengths)}")
        if weaknesses:
            parts.append(f"working to improve {', '.join(weaknesses)}")
        academic_areas_explanation = f"The student is {'; and '.join(parts)}."
    else:
        academic_areas_explanation = NO_ACADEMIC_AREAS_MESSAGE

    no_data = not (has_interests or has_motivation or has_academic_areas)

    logger.info(
        "Built exploration path explanation.",
        extra={
            "student_session_id": student_session_id,
            "has_interests": has_interests,
            "has_motivation": has_motivation,
            "has_academic_areas": has_academic_areas,
            "no_data": no_data,
        },
    )

    if no_data:
        return {
            "interests_explanation": NO_DATA_MESSAGE,
            "motivations_explanation": NO_DATA_MESSAGE,
            "academic_areas_explanation": NO_DATA_MESSAGE,
            "no_data": True,
        }

    return {
        "interests_explanation": interests_explanation,
        "motivations_explanation": motivations_explanation,
        "academic_areas_explanation": academic_areas_explanation,
        "no_data": False,
    }
