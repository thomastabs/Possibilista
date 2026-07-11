"""Legal framework document ingestion pipeline (Story 9389382).

Deterministic stub consistent with the rest of this repo's RAG surface (see
``natural_language_question.py`` and ``DETERMINISTIC_STUBS.md``) — no live embedding or LLM
calls. Validates a batch of raw candidate documents, derives a deterministic fake embedding for
each valid one, and persists them as ``Document`` rows. Corrupted documents are logged and
excluded from indexing; the batch keeps processing rather than aborting on the first failure.
"""

from __future__ import annotations

import logging
from typing import Any, TypedDict
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.document import EMBEDDING_DIMENSIONS, Document

logger = logging.getLogger(__name__)

LEGAL_FRAMEWORK_DOCUMENT_TYPE = "legal_framework"

_REQUIRED_FIELDS = ("title", "content", "source_url", "version_label")


class RawLegalFrameworkDocument(TypedDict, total=False):
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


def _validate_legal_framework_document(document: RawLegalFrameworkDocument) -> list[str]:
    """Return validation error messages; an empty list means the document is well-formed."""

    errors: list[str] = []
    for field in _REQUIRED_FIELDS:
        if not document.get(field):
            errors.append(f"Missing or empty required field '{field}'.")
    return errors


def _generate_embedding(content: str) -> list[float]:
    """Deterministic stand-in for a real embedding call — see DETERMINISTIC_STUBS.md.

    Derives a fixed-length numeric vector from the content's character codes so identical
    content always yields the same vector, without depending on any external service.
    """

    vector = [0.0] * EMBEDDING_DIMENSIONS
    if not content:
        return vector

    for index, char in enumerate(content):
        vector[index % EMBEDDING_DIMENSIONS] += ord(char)

    magnitude = max(vector) or 1.0
    return [round(value / magnitude, 6) for value in vector]


async def _upsert_document(
    db: AsyncSession, candidate: RawLegalFrameworkDocument, embedding: list[float]
) -> None:
    result = await db.execute(
        select(Document).where(Document.source_url == candidate["source_url"])
    )
    existing = result.scalar_one_or_none()

    if existing is not None:
        existing.title = candidate["title"]
        existing.content = candidate["content"]
        existing.document_type = LEGAL_FRAMEWORK_DOCUMENT_TYPE
        existing.version_label = candidate["version_label"]
        existing.indexed = True
        existing.indexing_errors = []
        existing.embedding = embedding
    else:
        db.add(
            Document(
                id=uuid4(),
                title=candidate["title"],
                content=candidate["content"],
                source_url=candidate["source_url"],
                document_type=LEGAL_FRAMEWORK_DOCUMENT_TYPE,
                version_label=candidate["version_label"],
                indexed=True,
                indexing_errors=[],
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
        validation_errors = _validate_legal_framework_document(candidate)

        if validation_errors:
            error_summary = "; ".join(validation_errors)
            logger.error(
                "Corrupted legal framework document detected; excluding from indexing.",
                extra={"document_id": document_id, "errors": validation_errors},
            )
            errors.append(f"{document_id}: {error_summary}")
            continue

        embedding = _generate_embedding(candidate["content"])

        try:
            await _upsert_document(db, candidate, embedding)
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
