"""Document indexing and retrieval endpoints (Stories 9389382, 9389384, 9389386, 9389388,
9389389, 9389391).

``auth: role:admin`` in the technical spec is not backed by a real role/permission system in
this repo slice (none exists yet for any endpoint) — enforced here as plain bearer-token
presence, same as every other endpoint. See ``DETERMINISTIC_STUBS.md``.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.profiling import get_db_session
from backend.services.document_ingestion_service import (
    ingest_higher_ed_requirements_documents,
    ingest_legal_framework_documents,
    ingest_secondary_track_definition_documents,
    reindex_all_official_documents,
)
from backend.services.document_retrieval_service import retrieve_relevant_documents
from backend.services.indexing_status_service import detect_updated_documents, get_indexing_status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
bearer_scheme = HTTPBearer(auto_error=True)

INDEXING_SUCCESS_MESSAGE_TEMPLATE = "Indexed {count} legal framework document(s)."
INDEXING_FAILURE_MESSAGE_TEMPLATE = (
    "Indexed {indexed_count} legal framework document(s); {error_count} document(s) were "
    "corrupted and excluded: {errors}"
)
INDEXING_UNEXPECTED_FAILURE_MESSAGE = "Unable to index legal framework documents."

SECONDARY_TRACK_DEFINITIONS_SUCCESS_MESSAGE_TEMPLATE = (
    "Indexed {count} secondary-track definition document(s)."
)
SECONDARY_TRACK_DEFINITIONS_FAILURE_MESSAGE_TEMPLATE = (
    "Indexed {indexed_count} secondary-track definition document(s); {error_count} document(s) "
    "were incomplete or corrupted: {errors}"
)
SECONDARY_TRACK_DEFINITIONS_UNEXPECTED_FAILURE_MESSAGE = (
    "Unable to index secondary-track definition documents."
)

HIGHER_ED_REQUIREMENTS_SUCCESS_MESSAGE_TEMPLATE = (
    "Indexed {count} higher-ed requirements document(s)."
)
HIGHER_ED_REQUIREMENTS_FAILURE_MESSAGE_TEMPLATE = (
    "Indexed {indexed_count} higher-ed requirements document(s); {error_count} document(s) "
    "were outdated or invalid and require updated versions before indexing: {errors}"
)
HIGHER_ED_REQUIREMENTS_UNEXPECTED_FAILURE_MESSAGE = (
    "Unable to index higher-ed requirements documents."
)

INDEX_UPDATE_RETENTION_MESSAGE = (
    "No new official document versions are available; the existing index was retained."
)
INDEX_UPDATE_SUCCESS_MESSAGE_TEMPLATE = (
    "Index refreshed — {count} document(s) updated across all official document types."
)
INDEX_UPDATE_PARTIAL_MESSAGE_TEMPLATE = (
    "Index refreshed — {indexed_count} document(s) updated; {error_count} document(s) "
    "failed to index: {errors}"
)
INDEX_UPDATE_UNEXPECTED_FAILURE_MESSAGE = "Unable to update the document index."


class DocumentIndexingResponse(BaseModel):
    status: str
    message: str


class IndexUpdateResponse(BaseModel):
    updated: bool
    message: str


class DocumentRetrievalResult(BaseModel):
    title: str
    content: str
    source_url: str


class DocumentRetrievalResponse(BaseModel):
    documents: list[DocumentRetrievalResult]
    no_source: bool


class DocumentIndexingStatusResponse(BaseModel):
    legal_framework_status: str
    exam_guide_status: str
    secondary_track_definitions_status: str
    higher_ed_requirements_status: str
    errors: list[str]


@router.post("/index-legal-framework", response_model=DocumentIndexingResponse)
async def post_index_legal_framework(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentIndexingResponse:
    logger.info(
        "Received legal framework document indexing request.",
        extra={"scheme": credentials.scheme},
    )

    try:
        result = await ingest_legal_framework_documents(db)
    except Exception:
        logger.exception("Legal framework document indexing failed unexpectedly.")
        return DocumentIndexingResponse(
            status="failed", message=INDEXING_UNEXPECTED_FAILURE_MESSAGE
        )

    indexed_count = result["indexed_count"]
    errors = result["errors"]

    if errors:
        status_value = "failed"
        message = INDEXING_FAILURE_MESSAGE_TEMPLATE.format(
            indexed_count=indexed_count,
            error_count=len(errors),
            errors="; ".join(errors),
        )
    else:
        status_value = "success"
        message = INDEXING_SUCCESS_MESSAGE_TEMPLATE.format(count=indexed_count)

    logger.info(
        "Legal framework document indexing request completed.",
        extra={
            "status": status_value,
            "indexed_count": indexed_count,
            "errors_count": len(errors),
        },
    )

    return DocumentIndexingResponse(status=status_value, message=message)


@router.post("/index-secondary-track-definitions", response_model=DocumentIndexingResponse)
async def post_index_secondary_track_definitions(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentIndexingResponse:
    logger.info(
        "Received secondary-track definitions indexing request.",
        extra={"scheme": credentials.scheme},
    )

    try:
        result = await ingest_secondary_track_definition_documents(db)
    except Exception:
        logger.exception("Secondary-track definitions indexing failed unexpectedly.")
        return DocumentIndexingResponse(
            status="failed", message=SECONDARY_TRACK_DEFINITIONS_UNEXPECTED_FAILURE_MESSAGE
        )

    indexed_count = result["indexed_count"]
    errors = result["errors"]

    if errors:
        status_value = "failed"
        message = SECONDARY_TRACK_DEFINITIONS_FAILURE_MESSAGE_TEMPLATE.format(
            indexed_count=indexed_count,
            error_count=len(errors),
            errors="; ".join(errors),
        )
    else:
        status_value = "success"
        message = SECONDARY_TRACK_DEFINITIONS_SUCCESS_MESSAGE_TEMPLATE.format(count=indexed_count)

    logger.info(
        "Secondary-track definitions indexing request completed.",
        extra={
            "status": status_value,
            "indexed_count": indexed_count,
            "errors_count": len(errors),
        },
    )

    return DocumentIndexingResponse(status=status_value, message=message)


@router.post("/index-higher-ed-requirements", response_model=DocumentIndexingResponse)
async def post_index_higher_ed_requirements(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentIndexingResponse:
    logger.info(
        "Received higher-ed requirements indexing request.",
        extra={"scheme": credentials.scheme},
    )

    try:
        result = await ingest_higher_ed_requirements_documents(db)
    except Exception:
        logger.exception("Higher-ed requirements indexing failed unexpectedly.")
        return DocumentIndexingResponse(
            status="failed", message=HIGHER_ED_REQUIREMENTS_UNEXPECTED_FAILURE_MESSAGE
        )

    indexed_count = result["indexed_count"]
    errors = result["errors"]

    if errors:
        status_value = "failed"
        message = HIGHER_ED_REQUIREMENTS_FAILURE_MESSAGE_TEMPLATE.format(
            indexed_count=indexed_count,
            error_count=len(errors),
            errors="; ".join(errors),
        )
    else:
        status_value = "success"
        message = HIGHER_ED_REQUIREMENTS_SUCCESS_MESSAGE_TEMPLATE.format(count=indexed_count)

    logger.info(
        "Higher-ed requirements indexing request completed.",
        extra={
            "status": status_value,
            "indexed_count": indexed_count,
            "errors_count": len(errors),
        },
    )

    return DocumentIndexingResponse(status=status_value, message=message)


@router.post("/index-update", response_model=IndexUpdateResponse)
async def post_index_update(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> IndexUpdateResponse:
    logger.info(
        "Received index update request.",
        extra={"scheme": credentials.scheme},
    )

    updates_available, outdated_sources = await detect_updated_documents(db)

    if not updates_available:
        logger.info("No updated document versions detected; retaining existing index.")
        return IndexUpdateResponse(updated=False, message=INDEX_UPDATE_RETENTION_MESSAGE)

    logger.info(
        "Updated document versions detected; refreshing index.",
        extra={"outdated_sources_count": len(outdated_sources)},
    )

    try:
        result = await reindex_all_official_documents(db)
    except Exception:
        logger.exception("Index update failed unexpectedly.")
        return IndexUpdateResponse(
            updated=False, message=INDEX_UPDATE_UNEXPECTED_FAILURE_MESSAGE
        )

    indexed_count = result["indexed_count"]
    errors = result["errors"]

    if errors:
        message = INDEX_UPDATE_PARTIAL_MESSAGE_TEMPLATE.format(
            indexed_count=indexed_count,
            error_count=len(errors),
            errors="; ".join(errors),
        )
    else:
        message = INDEX_UPDATE_SUCCESS_MESSAGE_TEMPLATE.format(count=indexed_count)

    logger.info(
        "Index update request completed.",
        extra={"indexed_count": indexed_count, "errors_count": len(errors)},
    )

    return IndexUpdateResponse(updated=True, message=message)


@router.get("/retrieve", response_model=DocumentRetrievalResponse)
async def get_documents_retrieve(
    query: str = Query(min_length=1),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentRetrievalResponse:
    logger.info(
        "Received document retrieval request.",
        extra={"query": query, "scheme": credentials.scheme},
    )

    result = await retrieve_relevant_documents(db, query)

    logger.info(
        "Document retrieval prepared.",
        extra={
            "query": query,
            "documents_count": len(result["documents"]),
            "no_source": result["no_source"],
        },
    )

    return DocumentRetrievalResponse(**result)


@router.get("/indexing-status", response_model=DocumentIndexingStatusResponse)
async def get_documents_indexing_status(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> DocumentIndexingStatusResponse:
    logger.info(
        "Received document indexing status request.",
        extra={"scheme": credentials.scheme},
    )

    result = await get_indexing_status(db)

    logger.info(
        "Document indexing status prepared.",
        extra={
            "legal_framework_status": result["legal_framework_status"],
            "exam_guide_status": result["exam_guide_status"],
            "secondary_track_definitions_status": result["secondary_track_definitions_status"],
            "higher_ed_requirements_status": result["higher_ed_requirements_status"],
            "errors_count": len(result["errors"]),
        },
    )

    return DocumentIndexingStatusResponse(**result)
