"""Conversational chat message service — distinguishes facts from interpretations."""

from __future__ import annotations

import logging
from typing import Any

from backend.services.natural_language_question import retrieve_official_documents

logger = logging.getLogger(__name__)

_INTERPRETATION_TERMS = {
    "should i",
    "what do you think",
    "recommend",
    "best for me",
    "which is better",
    "would you",
    "your opinion",
    "advice",
    "suggest",
}

_CRITICAL_DECISION_TERMS = {
    "change track",
    "switch track",
    "drop out",
    "equivalence",
    "special regime",
    "enroll",
    "enrollment",
    "contingent",
}


def _normalize_message(message: str) -> str:
    cleaned = message.strip()
    if not cleaned:
        raise ValueError("Message cannot be empty.")
    return cleaned


def _contains_any(text: str, terms: set[str]) -> bool:
    normalized = text.casefold()
    return any(term in normalized for term in terms)


def build_chat_response(message: str, session_id: str) -> dict[str, Any]:
    """Build a structured chat answer that separates documented facts from interpretation.

    Deterministic classification (no live LangChain/pgvector call in this repo slice),
    mirroring the pattern in ``natural_language_question.py``: reuses the same official
    document catalog for fact-grounding, then decides whether the question calls for an
    interpretative answer or flags that information is insufficient.
    """

    normalized_message = _normalize_message(message)

    logger.info(
        "Retrieving source-grounded documents for chat message.",
        extra={"session_id": session_id, "query": normalized_message},
    )
    documents = retrieve_official_documents(normalized_message)
    is_interpretative = _contains_any(normalized_message, _INTERPRETATION_TERMS)
    requires_confirmation = _contains_any(normalized_message, _CRITICAL_DECISION_TERMS)

    facts: list[str] = []
    interpretations: list[str] = []

    if documents:
        facts = [
            f"{document['title']} ({document['source_url']}): {document['content']}"
            for document in documents
        ]

    if is_interpretative:
        interpretations.append(
            "This is an interpretation based on general guidance, not a direct quote from "
            "official sources — confirm with a school counselor before deciding."
        )

    insufficient_info = not documents and not is_interpretative

    if insufficient_info:
        logger.info(
            "Insufficient information detected for chat message.",
            extra={"session_id": session_id},
        )
        answer = (
            "I cannot answer this question based on the current official sources available. "
            "Please consult a human advisor or school guidance counselor."
        )
    elif is_interpretative:
        document_titles = (
            ", ".join(f"'{document['title']}'" for document in documents)
            if documents
            else "the general secondary education guidance"
        )
        answer = (
            f"Based on {document_titles}, here is an interpretation: this is not a direct "
            "quote from official sources, so please confirm important decisions with a "
            "school counselor."
        )
    else:
        document_titles = ", ".join(f"'{document['title']}'" for document in documents)
        answer = (
            f"According to the official documents {document_titles} "
            f"(source: {documents[0]['source_url']}), {documents[0]['content']}"
        )

    logger.info(
        "Built chat message response.",
        extra={
            "session_id": session_id,
            "facts_count": len(facts),
            "interpretations_count": len(interpretations),
            "insufficient_info": insufficient_info,
            "requires_confirmation": requires_confirmation,
        },
    )

    return {
        "answer": answer,
        "facts": facts,
        "interpretations": interpretations,
        "insufficient_info": insufficient_info,
        "requires_confirmation": requires_confirmation,
        "session_id": session_id,
    }
