"""Family-focused exploration path and explanation services."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.explanation import Explanation
from backend.models.secondary_track import SecondaryTrack
from backend.services.natural_language_question import retrieve_official_documents
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
GENERIC_TRACK_SOURCE_URL = "https://www.dge.mec.pt/ensino-secundario"


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


async def get_fact_interpretation_distinction(db: AsyncSession, explanation_id: str) -> dict[str, Any]:
    """Fetch an Explanation record and expose its fact/interpretation distinction (Story 9389398).

    Returns ``unavailable_info=True`` with empty facts/interpretations when no record exists for
    the given ``explanation_id``, or when the lookup itself fails — this is how the system
    "states it lacks a basis to answer" rather than surfacing a 500.
    """

    try:
        result = await db.execute(
            select(Explanation).where(Explanation.explanation_id == explanation_id)
        )
        explanation = result.scalar_one_or_none()
    except SQLAlchemyError:
        logger.exception(
            "Failed to load explanation for fact-interpretation distinction.",
            extra={"explanation_id": explanation_id},
        )
        return {"facts": [], "interpretations": [], "unavailable_info": True}

    if explanation is None:
        logger.info(
            "No explanation record found for fact-interpretation distinction.",
            extra={"explanation_id": explanation_id},
        )
        return {"facts": [], "interpretations": [], "unavailable_info": True}

    logger.info(
        "Retrieved explanation fact-interpretation distinction.",
        extra={
            "explanation_id": explanation_id,
            "facts_count": len(explanation.facts),
            "interpretations_count": len(explanation.interpretations),
            "unavailable_info": explanation.unavailable_info,
        },
    )

    return {
        "facts": list(explanation.facts),
        "interpretations": list(explanation.interpretations),
        "unavailable_info": explanation.unavailable_info,
    }


def _score_secondary_track(
    track: SecondaryTrack, strengths: set[str], weaknesses: set[str]
) -> int:
    track_terms = {track.name.casefold()}
    if track.description:
        track_terms.update(track.description.casefold().split())
    discipline_terms = {discipline.discipline_name.casefold() for discipline in track.disciplines}
    all_terms = track_terms | discipline_terms

    strength_matches = sum(1 for value in strengths if value in all_terms)
    weakness_matches = sum(1 for value in weaknesses if value in all_terms)
    return (strength_matches * 3) - (weakness_matches * 2)


def _guidance_source_for_track(track: SecondaryTrack) -> str:
    documents = retrieve_official_documents(track.name)
    if documents:
        return documents[0]["source_url"]
    return GENERIC_TRACK_SOURCE_URL


async def get_guidance_outcomes(db: AsyncSession, student_session_id: str) -> dict[str, Any]:
    """Build source-grounded guidance recommendations for a student's academic planning (Story 9389397).

    Scores ``SecondaryTrack`` candidates against the student's recorded strengths/weaknesses —
    the same technique ``recommend_compatible_secondary_tracks`` in ``profiling.py`` uses — then
    pairs each recommended track with an official document reference. Returns
    ``pending=True`` with no recommendations when strengths/weaknesses haven't been recorded yet,
    no track scores above zero, or the lookup fails, mirroring ``profile_summary.py``'s
    "log and degrade gracefully" convention rather than raising.
    """

    strengths_record = await fetch_student_strengths_weaknesses(db, student_session_id)

    if strengths_record is None or not (strengths_record.strengths or strengths_record.weaknesses):
        logger.info(
            "No academic strengths/weaknesses recorded; guidance outcomes pending.",
            extra={"student_session_id": student_session_id},
        )
        return {"recommendations": [], "pending": True}

    normalized_strengths = {item.casefold() for item in strengths_record.strengths if item}
    normalized_weaknesses = {item.casefold() for item in strengths_record.weaknesses if item}

    try:
        result = await db.execute(
            select(SecondaryTrack).options(selectinload(SecondaryTrack.disciplines))
        )
        tracks = result.scalars().unique().all()
    except SQLAlchemyError:
        logger.exception(
            "Failed to load secondary tracks for guidance outcomes.",
            extra={"student_session_id": student_session_id},
        )
        return {"recommendations": [], "pending": True}

    scored_tracks = sorted(
        (
            (score, track)
            for track in tracks
            if (score := _score_secondary_track(track, normalized_strengths, normalized_weaknesses))
            > 0
        ),
        key=lambda item: (-item[0], item[1].name.lower()),
    )

    if not scored_tracks:
        logger.info(
            "No secondary track scored highly enough for guidance outcomes.",
            extra={"student_session_id": student_session_id},
        )
        return {"recommendations": [], "pending": True}

    recommendations = [
        {
            "text": (
                f"The {track.name} track is a strong match based on the student's recorded "
                "academic strengths and weaknesses."
                + (f" {track.description}" if track.description else "")
            ),
            "source": _guidance_source_for_track(track),
        }
        for _, track in scored_tracks[:3]
    ]

    logger.info(
        "Built guidance outcomes recommendations.",
        extra={
            "student_session_id": student_session_id,
            "recommendations_count": len(recommendations),
        },
    )

    return {"recommendations": recommendations, "pending": False}
