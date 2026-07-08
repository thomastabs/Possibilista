"""Conversational chat message service — distinguishes facts from interpretations."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chat_message import ChatMessage
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
    "special case",
    "exception",
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

    if requires_confirmation:
        logger.info(
            "Question flagged as requiring human or institutional confirmation.",
            extra={"session_id": session_id},
        )

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
        "topic_tokens": _topic_tokens(documents),
    }


def _topic_tokens(documents: list[Any]) -> list[str]:
    """Derive a topic identity for a turn from the official documents it matched."""

    return sorted({document["title"] for document in documents})


def _is_topic_change(previous_tokens: list[str], current_tokens: list[str]) -> bool:
    """A topic change is a disjoint, non-empty overlap between two turns' topic tokens.

    Either side being empty (a generic follow-up with no matched documents, or a first
    turn with no prior context) is not treated as a change — there is no signal to
    contradict continuity, so context is retained by default (Story 9389366).
    """

    previous_set = set(previous_tokens)
    current_set = set(current_tokens)
    if not previous_set or not current_set:
        return False
    return previous_set.isdisjoint(current_set)


def _message_id_str(message: ChatMessage | None) -> str | None:
    if message is None or message.id is None:
        return None
    return str(message.id)


async def get_last_chat_message(db: AsyncSession, session_id: str) -> ChatMessage | None:
    """Fetch the most recent ChatMessage for a session, used as dialogue context."""

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def build_chat_response_with_context(
    message: str,
    session_id: str,
    previous_message: ChatMessage | None,
) -> dict[str, Any]:
    """Build a chat response aware of the prior turn's dialogue context (Story 9389366).

    Retains the previous turn's topic tokens when the new message continues the same
    topic (or is too generic to signal a topic on its own), reusing its facts for a
    coherent follow-up answer instead of reporting insufficient information. Resets
    context — dropping the link to the previous turn — when an abrupt topic change is
    detected.
    """

    base_response = build_chat_response(message, session_id)
    current_tokens = base_response["topic_tokens"]
    previous_tokens = list(previous_message.context_tokens or []) if previous_message else []

    topic_changed = _is_topic_change(previous_tokens, current_tokens)

    if topic_changed:
        logger.info(
            "Dialogue topic change detected; resetting conversation context.",
            extra={"session_id": session_id},
        )
        base_response["context_tokens"] = current_tokens
        base_response["previous_message_id"] = None
        return base_response

    if base_response["insufficient_info"] and previous_message and previous_message.facts:
        logger.info(
            "Reusing prior dialogue context for a follow-up question.",
            extra={"session_id": session_id},
        )
        carried_facts = list(previous_message.facts)
        base_response["answer"] = "Continuing from the previous topic: " + " ".join(carried_facts)
        base_response["facts"] = carried_facts
        base_response["insufficient_info"] = False
        base_response["context_tokens"] = previous_tokens or current_tokens
        base_response["previous_message_id"] = _message_id_str(previous_message)
        return base_response

    base_response["context_tokens"] = current_tokens or previous_tokens
    base_response["previous_message_id"] = _message_id_str(previous_message)
    return base_response
