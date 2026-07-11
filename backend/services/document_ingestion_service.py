"""Document ingestion pipelines: legal framework (Story 9389382), general exam guide
(Story 9389384), secondary-track definitions (Story 9389386), and higher-ed course
requirements (Story 9389388).

Deterministic stub consistent with the rest of this repo's RAG surface (see
``natural_language_question.py`` and ``DETERMINISTIC_STUBS.md``) — no live embedding or LLM
calls; embeddings are generated via ``embedding_service.generate_embedding``. Legal framework
documents are ingested as a batch (corrupted ones logged and excluded, the rest still
processed); the exam guide is a single document (Story 9389384) — passing ``document=None``
simulates it being missing, so the system detects the absence rather than indexing nothing.
Secondary-track definition documents are also a batch, but unlike the other two, a document
missing *completeness* (not missing required fields, just not covering every required topic)
is still persisted — with ``indexed=False`` and its ``indexing_errors`` set — so it shows up
for admin review instead of vanishing silently (Story 9389386, scenario 2). Higher-ed
requirement documents are a batch too, with a fourth distinct failure mode: an *outdated*
version (older than the latest known version year) is excluded entirely and never persisted
at all (Story 9389388, scenario 2) — closer to legal framework's "corrupted" handling than to
secondary-track's "persist but flag" handling.
"""

from __future__ import annotations

import logging
import re
from typing import Any, TypedDict
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.document import Document
from backend.services.embedding_service import generate_embedding

logger = logging.getLogger(__name__)

LEGAL_FRAMEWORK_DOCUMENT_TYPE = "legal_framework"
EXAM_GUIDE_DOCUMENT_TYPE = "exam_guide"
EXAM_GUIDE_MISSING_MESSAGE = "General Exam Guide document is missing."
SECONDARY_TRACK_DEFINITIONS_DOCUMENT_TYPE = "secondary_track_definitions"
HIGHER_ED_REQUIREMENTS_DOCUMENT_TYPE = "higher_ed_requirements"
HIGHER_ED_REQUIREMENTS_LATEST_VERSION_YEAR = 2026

_REQUIRED_FIELDS = ("title", "content", "source_url", "version_label")
_COMPLETENESS_MARKERS = (
    "disciplines",
    "exam requirements",
    "discipline combinations",
    "higher education",
)


class RawLegalFrameworkDocument(TypedDict, total=False):
    id: str
    title: str
    content: str
    source_url: str
    version_label: str


class RawExamGuideDocument(TypedDict, total=False):
    id: str
    title: str
    content: str
    source_url: str
    version_label: str


class RawSecondaryTrackDefinitionDocument(TypedDict, total=False):
    id: str
    title: str
    content: str
    source_url: str
    version_label: str


class RawHigherEdRequirementDocument(TypedDict, total=False):
    id: str
    title: str
    content: str
    source_url: str
    version_label: str


_LEGAL_FRAMEWORK_DOCUMENT_CATALOG: list[RawLegalFrameworkDocument] = [
    {
        "id": "lei-54-2018",
        "title": "Lei n.º 54/2018 — Estatuto do Ensino Secundário",
        "content": (
            "Establishes the legal framework for secondary education tracks, including "
            "scientific-humanistic, professional, and specialized artistic pathways."
        ),
        "source_url": "https://www.dge.mec.pt/legislacao/lei-54-2018",
        "version_label": "2018-consolidated",
    },
    {
        "id": "portaria-235-a-2018",
        "title": "Portaria n.º 235-A/2018 — Cursos Profissionais",
        "content": (
            "Regulates the organization and operation of professional courses within "
            "secondary education."
        ),
        "source_url": "https://www.dge.mec.pt/legislacao/portaria-235-a-2018",
        "version_label": "2018-consolidated",
    },
]


def _validate_document_fields(document: dict[str, Any]) -> list[str]:
    """Return validation error messages; an empty list means the document is well-formed."""

    errors: list[str] = []
    for field in _REQUIRED_FIELDS:
        if not document.get(field):
            errors.append(f"Missing or empty required field '{field}'.")
    return errors


def _missing_completeness_markers(content: str) -> list[str]:
    """Return which required topics a secondary-track definition's content doesn't cover."""

    content_lower = content.casefold()
    return [marker for marker in _COMPLETENESS_MARKERS if marker not in content_lower]


def _version_year(version_label: str) -> int | None:
    match = re.match(r"(\d{4})", version_label)
    return int(match.group(1)) if match else None


def _is_outdated_higher_ed_requirements_version(version_label: str) -> bool:
    """A version older than the latest known year is outdated; an unrecognized format isn't
    treated as outdated, since there's no basis to judge it either way."""

    year = _version_year(version_label)
    if year is None:
        return False
    return year < HIGHER_ED_REQUIREMENTS_LATEST_VERSION_YEAR


async def _upsert_document(
    db: AsyncSession,
    candidate: dict[str, Any],
    document_type: str,
    embedding: list[float],
    *,
    indexed: bool = True,
    indexing_errors: list[str] | None = None,
) -> None:
    resolved_errors = indexing_errors or []

    result = await db.execute(
        select(Document).where(Document.source_url == candidate["source_url"])
    )
    existing = result.scalar_one_or_none()

    if existing is not None:
        existing.title = candidate["title"]
        existing.content = candidate["content"]
        existing.document_type = document_type
        existing.version_label = candidate["version_label"]
        existing.indexed = indexed
        existing.indexing_errors = resolved_errors
        existing.embedding = embedding
    else:
        db.add(
            Document(
                id=uuid4(),
                title=candidate["title"],
                content=candidate["content"],
                source_url=candidate["source_url"],
                document_type=document_type,
                version_label=candidate["version_label"],
                indexed=indexed,
                indexing_errors=resolved_errors,
                embedding=embedding,
            )
        )

    await db.commit()


async def ingest_legal_framework_documents(
    db: AsyncSession,
    documents: list[RawLegalFrameworkDocument] | None = None,
) -> dict[str, Any]:
    """Ingest legal framework documents: validate, embed, and persist the valid ones.

    Corrupted documents (missing required fields) are logged and excluded from indexing;
    the remaining documents in the batch are still processed rather than aborting the whole
    request (Story 9389382, scenario 2). Returns a summary the index-legal-framework endpoint
    reports back to the caller.
    """

    candidate_documents = (
        documents if documents is not None else _LEGAL_FRAMEWORK_DOCUMENT_CATALOG
    )

    indexed_count = 0
    errors: list[str] = []

    for candidate in candidate_documents:
        document_id = candidate.get("id", "<unknown>")
        validation_errors = _validate_document_fields(candidate)

        if validation_errors:
            error_summary = "; ".join(validation_errors)
            logger.error(
                "Corrupted legal framework document detected; excluding from indexing.",
                extra={"document_id": document_id, "errors": validation_errors},
            )
            errors.append(f"{document_id}: {error_summary}")
            continue

        embedding = generate_embedding(candidate["content"])

        try:
            await _upsert_document(db, candidate, LEGAL_FRAMEWORK_DOCUMENT_TYPE, embedding)
        except SQLAlchemyError:
            await db.rollback()
            logger.exception(
                "Failed to persist legal framework document.",
                extra={"document_id": document_id},
            )
            errors.append(f"{document_id}: database persistence failed.")
            continue

        indexed_count += 1
        logger.info(
            "Indexed legal framework document.",
            extra={"document_id": document_id, "source_url": candidate["source_url"]},
        )

    logger.info(
        "Legal framework document ingestion complete.",
        extra={
            "indexed_count": indexed_count,
            "errors_count": len(errors),
            "candidates_count": len(candidate_documents),
        },
    )

    return {"indexed_count": indexed_count, "errors": errors}


_EXAM_GUIDE_DOCUMENT: RawExamGuideDocument = {
    "id": "general-exam-guide-2026",
    "title": "General Exam Guide — Provas de Aferição e Exames Nacionais",
    "content": (
        "Describes the national exam calendar, subject-specific exam structure, grading "
        "criteria, and special exam arrangements for secondary education students."
    ),
    "source_url": "https://www.dge.mec.pt/exames-nacionais",
    "version_label": "2026-edition",
}


async def ingest_exam_guide_document(
    db: AsyncSession,
    document: RawExamGuideDocument | None = _EXAM_GUIDE_DOCUMENT,
) -> dict[str, Any]:
    """Ingest the General Exam Guide document: validate, embed, and persist it.

    Unlike the legal framework batch, there is exactly one exam guide document
    (Story 9389384) — pass ``document=None`` to simulate it being missing (Gherkin scenario
    2): the system logs the absence for administrator notification and does not proceed
    with embedding or persistence. The document being missing (or malformed) is surfaced to
    administrators via ``indexing_status_service.get_indexing_status`` rather than a
    separate alerting channel, since none exists in this repo slice.
    """

    if document is None:
        logger.error(
            "General Exam Guide document is missing; cannot index.",
            extra={"document_type": EXAM_GUIDE_DOCUMENT_TYPE},
        )
        return {"indexed": False, "errors": [EXAM_GUIDE_MISSING_MESSAGE]}

    document_id = document.get("id", "<unknown>")
    validation_errors = _validate_document_fields(document)

    if validation_errors:
        error_summary = "; ".join(validation_errors)
        logger.error(
            "Corrupted General Exam Guide document detected; excluding from indexing.",
            extra={"document_id": document_id, "errors": validation_errors},
        )
        return {"indexed": False, "errors": [f"{document_id}: {error_summary}"]}

    embedding = generate_embedding(document["content"])

    try:
        await _upsert_document(db, document, EXAM_GUIDE_DOCUMENT_TYPE, embedding)
    except SQLAlchemyError:
        await db.rollback()
        logger.exception(
            "Failed to persist General Exam Guide document.",
            extra={"document_id": document_id},
        )
        return {"indexed": False, "errors": [f"{document_id}: database persistence failed."]}

    logger.info(
        "Indexed General Exam Guide document.",
        extra={"document_id": document_id, "source_url": document["source_url"]},
    )

    return {"indexed": True, "errors": []}


_SECONDARY_TRACK_DEFINITIONS_CATALOG: list[RawSecondaryTrackDefinitionDocument] = [
    {
        "id": "secondary-track-definitions-2026",
        "title": "Secondary Track Definitions — Disciplines, Exams, and Higher-Ed Impact",
        "content": (
            "Defines each secondary track's disciplines, exam requirements, discipline "
            "combinations (trienais, bienais, anuais), and higher education impact for "
            "progression eligibility."
        ),
        "source_url": "https://www.dge.mec.pt/definicoes-cursos-secundarios",
        "version_label": "2026-edition",
    },
]


async def ingest_secondary_track_definition_documents(
    db: AsyncSession,
    documents: list[RawSecondaryTrackDefinitionDocument] | None = None,
) -> dict[str, Any]:
    """Ingest secondary-track definition documents: validate, embed, and persist them.

    Two distinct failure modes (Story 9389386):
    - Missing required fields (title/content/source_url/version_label): the document can't
      form a row at all, so it's logged and excluded entirely — same as legal framework.
    - Missing *completeness* (required fields present, but the content doesn't cover
      disciplines/exam requirements/discipline combinations/higher-ed impact): the document
      **is** persisted, with ``indexed=False`` and its ``indexing_errors`` set, so it's
      flagged for admin review (scenario 2) instead of vanishing silently.
    """

    candidate_documents = (
        documents if documents is not None else _SECONDARY_TRACK_DEFINITIONS_CATALOG
    )

    indexed_count = 0
    errors: list[str] = []

    for candidate in candidate_documents:
        document_id = candidate.get("id", "<unknown>")
        field_errors = _validate_document_fields(candidate)

        if field_errors:
            error_summary = "; ".join(field_errors)
            logger.error(
                "Corrupted secondary-track definition document detected; excluding from "
                "indexing.",
                extra={"document_id": document_id, "errors": field_errors},
            )
            errors.append(f"{document_id}: {error_summary}")
            continue

        embedding = generate_embedding(candidate["content"])
        missing_markers = _missing_completeness_markers(candidate["content"])

        if missing_markers:
            completeness_error = (
                "Incomplete secondary-track definition: missing "
                + ", ".join(missing_markers)
                + "."
            )
            logger.error(
                "Incomplete secondary-track definition document detected; flagging for "
                "review.",
                extra={"document_id": document_id, "errors": [completeness_error]},
            )
            try:
                await _upsert_document(
                    db,
                    candidate,
                    SECONDARY_TRACK_DEFINITIONS_DOCUMENT_TYPE,
                    embedding,
                    indexed=False,
                    indexing_errors=[completeness_error],
                )
            except SQLAlchemyError:
                await db.rollback()
                logger.exception(
                    "Failed to persist incomplete secondary-track definition document.",
                    extra={"document_id": document_id},
                )
            errors.append(f"{document_id}: {completeness_error}")
            continue

        try:
            await _upsert_document(
                db, candidate, SECONDARY_TRACK_DEFINITIONS_DOCUMENT_TYPE, embedding
            )
        except SQLAlchemyError:
            await db.rollback()
            logger.exception(
                "Failed to persist secondary-track definition document.",
                extra={"document_id": document_id},
            )
            errors.append(f"{document_id}: database persistence failed.")
            continue

        indexed_count += 1
        logger.info(
            "Indexed secondary-track definition document.",
            extra={"document_id": document_id, "source_url": candidate["source_url"]},
        )

    logger.info(
        "Secondary-track definition document ingestion complete.",
        extra={
            "indexed_count": indexed_count,
            "errors_count": len(errors),
            "candidates_count": len(candidate_documents),
        },
    )

    return {"indexed_count": indexed_count, "errors": errors}


_HIGHER_ED_REQUIREMENTS_CATALOG: list[RawHigherEdRequirementDocument] = [
    {
        "id": "higher-ed-requirements-2026",
        "title": "Higher Education Course Requirements — Entrance Exams and Admission Averages",
        "content": (
            "Describes entrance exam requirements, exam weights, and admission averages for "
            "higher education courses compatible with each secondary track."
        ),
        "source_url": "https://www.dge.mec.pt/requisitos-ensino-superior",
        "version_label": "2026-edition",
    },
]


async def ingest_higher_ed_requirements_documents(
    db: AsyncSession,
    documents: list[RawHigherEdRequirementDocument] | None = None,
) -> dict[str, Any]:
    """Ingest higher-ed course requirement documents: validate freshness, embed, and persist.

    Two failure modes, both resulting in full exclusion (Story 9389388):
    - Missing required fields: same as legal framework — no row to form, logged and skipped.
    - Outdated version (older than ``HIGHER_ED_REQUIREMENTS_LATEST_VERSION_YEAR``): logged and
      skipped — "the system requires updated versions before indexing" (scenario 2) means no
      Document row is persisted or marked indexed for an outdated document at all, unlike
      secondary-track definitions' "incomplete but persisted" handling.
    """

    candidate_documents = (
        documents if documents is not None else _HIGHER_ED_REQUIREMENTS_CATALOG
    )

    indexed_count = 0
    errors: list[str] = []

    for candidate in candidate_documents:
        document_id = candidate.get("id", "<unknown>")
        field_errors = _validate_document_fields(candidate)

        if field_errors:
            error_summary = "; ".join(field_errors)
            logger.error(
                "Corrupted higher-ed requirements document detected; excluding from "
                "indexing.",
                extra={"document_id": document_id, "errors": field_errors},
            )
            errors.append(f"{document_id}: {error_summary}")
            continue

        version_label = candidate["version_label"]
        if _is_outdated_higher_ed_requirements_version(version_label):
            outdated_error = (
                f"Outdated version '{version_label}'; requires a version from "
                f"{HIGHER_ED_REQUIREMENTS_LATEST_VERSION_YEAR} or later."
            )
            logger.error(
                "Outdated higher-ed requirements document detected; excluding from "
                "indexing.",
                extra={
                    "document_id": document_id,
                    "title": candidate.get("title", "<unknown>"),
                    "version_label": version_label,
                },
            )
            errors.append(f"{document_id}: {outdated_error}")
            continue

        embedding = generate_embedding(candidate["content"])

        try:
            await _upsert_document(
                db, candidate, HIGHER_ED_REQUIREMENTS_DOCUMENT_TYPE, embedding
            )
        except SQLAlchemyError:
            await db.rollback()
            logger.exception(
                "Failed to persist higher-ed requirements document.",
                extra={"document_id": document_id},
            )
            errors.append(f"{document_id}: database persistence failed.")
            continue

        indexed_count += 1
        logger.info(
            "Indexed higher-ed requirements document.",
            extra={"document_id": document_id, "source_url": candidate["source_url"]},
        )

    logger.info(
        "Higher-ed requirements document ingestion complete.",
        extra={
            "indexed_count": indexed_count,
            "errors_count": len(errors),
            "candidates_count": len(candidate_documents),
        },
    )

    return {"indexed_count": indexed_count, "errors": errors}
