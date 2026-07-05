"""Natural language question guidance service."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_SECONDARY_CONTEXT_TERMS = {
    "secondary",
    "education",
    "track",
    "tracks",
    "course",
    "courses",
    "school",
    "9.º ano",
    "9 ano",
    "9th grade",
}

_SPECIFIC_TRACK_TERMS = {
    "scientific-humanistic",
    "scientific humanistic",
    "professional",
    "artistic",
    "specialized artistic",
    "specialised artistic",
    "vocational",
}

_CLARIFICATION_OPTIONS = [
    "Scientific-humanistic tracks",
    "Professional tracks",
    "Specialized artistic tracks",
]

_TRACK_SUMMARY = (
    "The official secondary education guidance highlights scientific-humanistic, "
    "professional, and specialized artistic tracks as the main pathways."
)

_OUT_OF_SCOPE_SUGGESTION = (
    "This assistant only covers Portuguese secondary education tracks. Please consult "
    "a human advisor or school guidance counselor."
)


def _normalize_question(question: str) -> str:
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("Question cannot be empty.")
    return cleaned


def _contains_any(text: str, terms: set[str]) -> bool:
    normalized = text.casefold()
    return any(term.casefold() in normalized for term in terms)


def _classify_question(question: str) -> str:
    normalized = question.casefold()

    if _contains_any(normalized, {"weather", "movie", "sports", "recipe", "travel", "music", "game"}):
        return "out_of_scope"

    if not _contains_any(normalized, _SECONDARY_CONTEXT_TERMS):
        return "out_of_scope"

    if _contains_any(normalized, _SPECIFIC_TRACK_TERMS) or _contains_any(
        normalized,
        {"available tracks", "what tracks", "compare", "difference", "differences", "which track"},
    ):
        return "clear"

    return "ambiguous"


def _build_clear_answer(question: str) -> str:
    if _contains_any(question, {"compare", "difference", "differences"}):
        return (
            "According to the official secondary education guidance, the main track families are "
            "scientific-humanistic, professional, and specialized artistic. The guidance material "
            "compares them by focus, practical training, and progression to higher education."
        )

    return f"{_TRACK_SUMMARY} Ask about one track if you want a more detailed, source-based explanation."


def _build_clarification_options(question: str) -> list[str]:
    normalized = question.casefold()
    if "professional" in normalized:
        return ["What do professional tracks include?", "What subjects are in professional tracks?"]
    if "artistic" in normalized:
        return ["What do specialized artistic tracks include?", "What subjects are in artistic tracks?"]
    if "scientific" in normalized or "humanistic" in normalized:
        return [
            "What do scientific-humanistic tracks include?",
            "What subjects are in scientific-humanistic tracks?",
        ]
    return _CLARIFICATION_OPTIONS.copy()


async def answer_natural_language_question(
    question: str,
    session_id: str,
) -> dict[str, Any]:
    """Return a structured response for a student question."""

    normalized_question = _normalize_question(question)
    classification = _classify_question(normalized_question)

    logger.info(
        "Processing natural language question.",
        extra={
            "session_id": session_id,
            "question": normalized_question,
            "classification": classification,
        },
    )

    if classification == "out_of_scope":
        logger.info(
            "Natural language question classified as out of scope.",
            extra={"session_id": session_id},
        )
        return {
            "answer": "I can only answer questions about Portuguese secondary education tracks.",
            "clarification_needed": False,
            "clarification_options": [],
            "out_of_scope": True,
            "suggestion": _OUT_OF_SCOPE_SUGGESTION,
            "session_id": session_id,
        }

    if classification == "ambiguous":
        clarification_options = _build_clarification_options(normalized_question)
        logger.info(
            "Natural language question requires clarification.",
            extra={
                "session_id": session_id,
                "clarification_options_count": len(clarification_options),
            },
        )
        return {
            "answer": (
                "Your question is a bit broad. Please choose one of the options below so I can "
                "answer using the official secondary education guidance."
            ),
            "clarification_needed": True,
            "clarification_options": clarification_options,
            "out_of_scope": False,
            "suggestion": "Select the track or topic you want me to clarify.",
            "session_id": session_id,
        }

    answer = _build_clear_answer(normalized_question)
    logger.info(
        "Natural language question classified as clear.",
        extra={"session_id": session_id},
    )
    return {
        "answer": answer,
        "clarification_needed": False,
        "clarification_options": [],
        "out_of_scope": False,
        "suggestion": "",
        "session_id": session_id,
    }
