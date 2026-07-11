"""Conversational chat message service — distinguishes facts from interpretations."""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chat_message import ChatMessage
from backend.services.natural_language_question import retrieve_official_documents

logger = logging.getLogger(__name__)

_QUESTION_WORDS = {"what", "which", "how", "when", "where", "why", "who"}

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
    matches_critical_terms = _contains_any(normalized_message, _CRITICAL_DECISION_TERMS)

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
    requires_confirmation = matches_critical_terms or insufficient_info or is_interpretative

    if requires_confirmation:
        logger.info(
            "Question flagged as requiring human or institutional confirmation.",
            extra={
                "session_id": session_id,
                "matches_critical_terms": matches_critical_terms,
                "insufficient_info": insufficient_info,
            },
        )

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
        "is_fact": bool(facts),
        "is_interpretation": bool(interpretations),
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
        base_response["is_fact"] = bool(carried_facts)
        base_response["context_tokens"] = previous_tokens or current_tokens
        base_response["previous_message_id"] = _message_id_str(previous_message)
        return base_response

    base_response["context_tokens"] = current_tokens or previous_tokens
    base_response["previous_message_id"] = _message_id_str(previous_message)
    return base_response


def segment_intents(message: str) -> list[str]:
    """Split a compound question into its distinct intents (Story 9389368).

    Two heuristics, tried in order:
    1. Multiple "?" characters split the message outright into that many parts.
    2. A single-sentence question joined by "and" is split only when the second half
       itself starts with a question word — so a plain conjunction inside one intent
       ("professional and artistic tracks") is left alone, and only a genuine second
       question ("... and what subjects does it include?") is segmented.

    A straightforward question that matches neither heuristic returns as one segment,
    so the single-intent path is unchanged from before this story.
    """

    normalized = message.strip()

    if normalized.count("?") > 1:
        parts = [part.strip() for part in normalized.split("?") if part.strip()]
        return [f"{part}?" for part in parts]

    split = re.split(r"\band\b", normalized, maxsplit=1)
    if len(split) == 2:
        first, second = (part.strip() for part in split)
        second_first_word = second.split(" ", 1)[0].casefold().strip("?,.") if second else ""
        if first and second and second_first_word in _QUESTION_WORDS:
            return [first, second]

    return [normalized]


def build_chat_response_for_message(
    message: str,
    session_id: str,
    previous_message: ChatMessage | None,
) -> dict[str, Any]:
    """Top-level chat response builder: segments intents, then dispatches each part.

    A straightforward, single-intent message is unchanged from before this story — it
    goes straight through the dialogue-context-aware ``build_chat_response_with_context``.
    A compound/multi-part question is segmented (Story 9389368) and each part is answered
    independently via the context-blind ``build_chat_response`` (dialogue-context carry-
    forward is reserved for the common single-intent case), then combined: answers are
    numbered and joined, facts/interpretations concatenated across parts,
    insufficient_info only when *every* part lacked a basis, requires_confirmation when
    *any* part needs it.
    """

    normalized_message = _normalize_message(message)
    segments = segment_intents(normalized_message)

    if len(segments) == 1:
        return build_chat_response_with_context(segments[0], session_id, previous_message)

    logger.info(
        "Compound question segmented into multiple intents.",
        extra={"session_id": session_id, "segments_count": len(segments)},
    )

    segment_responses = [build_chat_response(segment, session_id) for segment in segments]

    answer = " ".join(
        f"{index}) {response['answer']}" for index, response in enumerate(segment_responses, start=1)
    )
    facts = [fact for response in segment_responses for fact in response["facts"]]
    interpretations = [
        interpretation
        for response in segment_responses
        for interpretation in response["interpretations"]
    ]
    insufficient_info = all(response["insufficient_info"] for response in segment_responses)
    requires_confirmation = any(response["requires_confirmation"] for response in segment_responses)
    topic_tokens = sorted({token for response in segment_responses for token in response["topic_tokens"]})

    logger.info(
        "Built combined multi-intent chat response.",
        extra={
            "session_id": session_id,
            "segments_count": len(segments),
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
        "is_fact": bool(facts),
        "is_interpretation": bool(interpretations),
        "session_id": session_id,
        "topic_tokens": topic_tokens,
        "context_tokens": topic_tokens,
        "previous_message_id": None,
    }
