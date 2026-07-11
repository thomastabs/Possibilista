import asyncio

from backend.services.document_ingestion_service import ingest_legal_framework_documents
from backend.services.document_retrieval_service import retrieve_relevant_documents


class IngestionDummyResult:
    def scalar_one_or_none(self):
        return None


class IngestionDummyDB:
    def __init__(self):
        self.added = []

    async def execute(self, statement):
        return IngestionDummyResult()

    def add(self, record):
        self.added.append(record)

    async def commit(self):
        pass

    async def rollback(self):
        pass


class RetrievalDummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class RetrievalDummyDB:
    def __init__(self, documents):
        self.documents = documents

    async def execute(self, statement):
        return RetrievalDummyResult(self.documents)


def test_ingested_documents_are_retrievable_after_indexing():
    """Story 9389389's precondition ("the system has indexed official documents") holds
    directly against what an ingestion pipeline actually persists — not a separate fixture."""

    ingestion_db = IngestionDummyDB()
    ingestion_result = asyncio.run(ingest_legal_framework_documents(ingestion_db))

    assert ingestion_result["indexed_count"] == len(ingestion_db.added)
    assert all(document.indexed for document in ingestion_db.added)
    assert all(document.embedding is not None for document in ingestion_db.added)

    retrieval_db = RetrievalDummyDB(documents=ingestion_db.added)
    retrieval_result = asyncio.run(
        retrieve_relevant_documents(retrieval_db, "What are the professional tracks?")
    )

    assert retrieval_result["no_source"] is False
    retrieved_titles = {document["title"] for document in retrieval_result["documents"]}
    ingested_titles = {document.title for document in ingestion_db.added}
    assert retrieved_titles == ingested_titles
