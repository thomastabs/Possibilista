"""Vector-similarity document retrieval (Story 9389389).

Deterministic-embedding stub (see ``DETERMINISTIC_STUBS.md``) — the query is embedded with
the same ``generate_embedding`` used at ingestion time, then compared against indexed
``Document`` rows via pgvector's L2 distance (the ``<->`` operator, exposed here as
``Column.l2_distance``), so retrieval is genuinely similarity-based rather than a keyword
filter, consistent with what the four ingestion pipelines already store.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.document import Document
from backend.services.embedding_service import generate_embedding

logger = logging.getLogger(__name__)

DEFAULT_RETRIEVAL_LIMIT = 3


async def retrieve_relevant_documents(
    db: AsyncSession, query: str, limit: int = DEFAULT_RETRIEVAL_LIMIT
) -> dict[str, Any]:
    """Return the top ``limit`` indexed documents most similar to ``query``.

    ``no_source=True`` with an empty list when nothing indexed matches, or when the lookup
    itself fails — no official source is claimed rather than surfacing a 500 (Story 9389389,
    scenario 2).
    """

    query_embedding = generate_embedding(query)

    try:
        result = await db.execute(
            select(Document)
            .where(Document.indexed.is_(True), Document.embedding.is_not(None))
            .order_by(Document.embedding.l2_distance(query_embedding))
            .limit(limit)
        )
        documents = list(result.scalars().all())
    except SQLAlchemyError:
        logger.exception("Failed to retrieve relevant documents.", extra={"query": query})
        return {"documents": [], "no_source": True}

    if not documents:
        logger.info(
            "No relevant documents found for query.",
            extra={"query": query},
        )
        return {"documents": [], "no_source": True}

    logger.info(
        "Retrieved relevant documents for query.",
        extra={"query": query, "documents_count": len(documents)},
    )

    return {
        "documents": [
            {
                "title": document.title,
                "content": document.content,
                "source_url": document.source_url,
            }
            for document in documents
        ],
        "no_source": False,
    }
