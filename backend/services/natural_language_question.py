"""Natural language question guidance service."""

from __future__ import annotations

import logging
import inspect
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, TypedDict

logger = logging.getLogger(__name__)


class OfficialDocument(TypedDict):
    title: str
    content: str
    source_url: str

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

_OUT_OF_SCOPE_SUGGESTION = (
    "This assistant only covers Portuguese secondary education tracks. Please consult "
    "a human advisor or school guidance counselor."
)

_OFFICIAL_DOCUMENT_CATALOG: list[dict[str, Any]] = [
    {
        "title": "Scientific-humanistic Courses Guidance",
        "content": (
            "Scientific-humanistic courses focus on sciences, languages, and humanities and "
            "prepare students primarily for higher education."
        ),
        "source_url": "https://www.dge.mec.pt/cursos-cientifico-humanisticos",
        "keywords": {"scientific", "humanistic", "sciences", "humanities", "higher education"},
    },
    {
        "title": "Professional Courses Guidance",
        "content": (
            "Professional courses combine general education with technical and workplace training "
            "and lead to a secondary qualification and professional preparation."
        ),
        "source_url": "https://www.dge.mec.pt/cursos-profissionais",
        "keywords": {"professional", "technical", "workplace", "qualification", "training"},
    },
    {
        "title": "Specialized Artistic Courses Guidance",
        "content": (
            "Specialized artistic courses focus on artistic development and practical training in "
            "art-related disciplines."
        ),
        "source_url": "https://www.dge.mec.pt/cursos-artisticos-especializados",
        "keywords": {"artistic", "arts", "art", "specialized", "specialised"},
    },
    {
        "title": "Secondary Education Overview",
        "content": (
            "The official secondary education overview summarizes the main pathways available to "
            "students and explains how to choose among them."
        ),
        "source_url": "https://www.dge.mec.pt/ensino-secundario",
        "keywords": {"overview", "available tracks", "what tracks", "secondary education", "choose"},
    },
]


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

    if (
        _contains_any(normalized, _SPECIFIC_TRACK_TERMS)
        or ("available" in normalized and "track" in normalized)
        or _contains_any(
            normalized,
            {"what tracks", "compare", "difference", "differences", "which track"},
        )
    ):
        return "clear"

    return "ambiguous"


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


def _document_matches(question: str, document: dict[str, Any]) -> bool:
    normalized = question.casefold()
    keywords = document["keywords"]
    return any(keyword.casefold() in normalized for keyword in keywords)


def retrieve_official_documents(question: str, limit: int = 3) -> list[OfficialDocument]:
    """Return a small set of official documents that match the student question."""

    logger.info(
        "Retrieving official documents for natural language question.",
        extra={"question": question, "limit": limit},
    )

    candidate_documents = [
        document
        for document in _OFFICIAL_DOCUMENT_CATALOG
        if _document_matches(question, document)
    ]

    if not candidate_documents and _contains_any(
        question,
        {"available tracks", "what tracks", "secondary education", "secondary tracks"},
    ):
        candidate_documents = _OFFICIAL_DOCUMENT_CATALOG.copy()

    selected_documents = candidate_documents[:limit]

    logger.info(
        "Official document retrieval completed.",
        extra={
            "question": question,
            "documents_count": len(selected_documents),
        },
    )

    return [
        {
            "title": document["title"],
            "content": document["content"],
            "source_url": document["source_url"],
        }
        for document in selected_documents
    ]


async def _resolve_official_documents(
    question: str,
    document_retriever: Callable[[str], Sequence[OfficialDocument] | Awaitable[Sequence[OfficialDocument]]] | None,
) -> list[OfficialDocument]:
    retriever = document_retriever or retrieve_official_documents
    documents = retriever(question)
    if inspect.isawaitable(documents):
        resolved = await documents
    else:
        resolved = documents
    return [
        {
            "title": document["title"],
            "content": document["content"],
            "source_url": document["source_url"],
        }
        for document in resolved
    ]


async def answer_natural_language_question(
    question: str,
    session_id: str,
    document_retriever: Callable[[str], Sequence[OfficialDocument] | Awaitable[Sequence[OfficialDocument]]] | None = None,
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
            "documents": [],
            "no_source": True,
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
            "documents": [],
            "no_source": True,
        }

    documents = await _resolve_official_documents(normalized_question, document_retriever)
    no_source = len(documents) == 0

    if no_source:
        answer = (
            "I can answer your question at a high level, but I could not find an official document "
            "that directly matches it right now."
        )
    else:
        document_titles = ", ".join(f"'{document['title']}'" for document in documents)
        answer = (
            f"According to the official documents {document_titles}, "
            "the main secondary education pathways are scientific-humanistic, professional, "
            "and specialized artistic tracks."
        )

    logger.info(
        "Natural language question classified as clear.",
        extra={"session_id": session_id, "documents_count": len(documents), "no_source": no_source},
    )
    return {
        "answer": answer,
        "clarification_needed": False,
        "clarification_options": [],
        "out_of_scope": False,
        "suggestion": "",
        "session_id": session_id,
        "documents": documents,
        "no_source": no_source,
    }
