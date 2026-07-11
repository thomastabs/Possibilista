import asyncio
import logging

from backend.models.document import EMBEDDING_DIMENSIONS
from backend.services.document_ingestion_service import (
    LEGAL_FRAMEWORK_DOCUMENT_TYPE,
    _generate_embedding,
    ingest_legal_framework_documents,
)


class DummyResult:
    def __init__(self, record):
        self._record = record

    def scalar_one_or_none(self):
        return self._record


class DummyDB:
    def __init__(self):
        self.added = []
        self.committed = 0
        self.rolled_back = 0
        self.existing_document = None

    async def execute(self, statement):
        return DummyResult(self.existing_document)

    def add(self, record):
        self.added.append(record)

    async def commit(self):
        self.committed += 1

    async def rollback(self):
        self.rolled_back += 1


VALID_DOCUMENT = {
    "id": "valid-doc",
    "title": "Lei n.º 54/2018",
    "content": "Establishes the legal framework for secondary education tracks.",
    "source_url": "https://www.dge.mec.pt/legislacao/lei-54-2018",
    "version_label": "2018-consolidated",
}

CORRUPTED_DOCUMENT = {
    "id": "corrupted-doc",
    "title": "",
    "content": "",
    "source_url": "",
    "version_label": "",
}


def test_legal_framework_ingestion_indexes_valid_documents_and_makes_them_searchable():
    db = DummyDB()

    result = asyncio.run(ingest_legal_framework_documents(db, [VALID_DOCUMENT]))

    assert result["indexed_count"] == 1
    assert result["errors"] == []
    assert len(db.added) == 1
    indexed_document = db.added[0]
    assert indexed_document.indexed is True
    assert indexed_document.content == VALID_DOCUMENT["content"]
    assert indexed_document.document_type == LEGAL_FRAMEWORK_DOCUMENT_TYPE
    assert indexed_document.embedding is not None
    assert len(indexed_document.embedding) == 8


def test_legal_framework_ingestion_detects_corrupted_documents():
    db = DummyDB()

    result = asyncio.run(ingest_legal_framework_documents(db, [CORRUPTED_DOCUMENT]))

    assert result["indexed_count"] == 0
    assert len(result["errors"]) == 1
    assert "corrupted-doc" in result["errors"][0]


def test_legal_framework_ingestion_logs_error_for_corrupted_documents(caplog):
    db = DummyDB()

    with caplog.at_level(logging.ERROR):
        asyncio.run(ingest_legal_framework_documents(db, [CORRUPTED_DOCUMENT]))

    assert any(
        "Corrupted legal framework document detected" in record.message
        for record in caplog.records
    )


def test_legal_framework_ingestion_excludes_corrupted_documents_from_indexing():
    db = DummyDB()

    asyncio.run(ingest_legal_framework_documents(db, [VALID_DOCUMENT, CORRUPTED_DOCUMENT]))

    assert len(db.added) == 1
    assert db.added[0].source_url == VALID_DOCUMENT["source_url"]


def test_legal_framework_ingestion_continues_processing_after_a_corrupted_document():
    db = DummyDB()
    second_valid = {
        "id": "second-valid-doc",
        "title": "Portaria n.º 235-A/2018",
        "content": "Regulates professional courses within secondary education.",
        "source_url": "https://www.dge.mec.pt/legislacao/portaria-235-a-2018",
        "version_label": "2018-consolidated",
    }

    result = asyncio.run(
        ingest_legal_framework_documents(db, [VALID_DOCUMENT, CORRUPTED_DOCUMENT, second_valid])
    )

    assert result["indexed_count"] == 2
    assert len(result["errors"]) == 1
    assert len(db.added) == 2


def test_generate_embedding_is_deterministic_for_identical_content():
    content = "Establishes the legal framework for secondary education tracks."

    first = _generate_embedding(content)
    second = _generate_embedding(content)

    assert first == second
    assert len(first) == EMBEDDING_DIMENSIONS


def test_generate_embedding_differs_for_different_content():
    embedding_one = _generate_embedding("Establishes the legal framework for secondary tracks.")
    embedding_two = _generate_embedding("Regulates professional courses within secondary education.")

    assert embedding_one != embedding_two


def test_legal_framework_ingestion_stores_distinct_embeddings_for_distinct_documents():
    db = DummyDB()
    second_valid = {
        "id": "second-valid-doc",
        "title": "Portaria n.º 235-A/2018",
        "content": "Regulates professional courses within secondary education.",
        "source_url": "https://www.dge.mec.pt/legislacao/portaria-235-a-2018",
        "version_label": "2018-consolidated",
    }

    asyncio.run(ingest_legal_framework_documents(db, [VALID_DOCUMENT, second_valid]))

    embeddings = [document.embedding for document in db.added]
    assert len(embeddings) == 2
    assert embeddings[0] != embeddings[1]
    assert all(len(embedding) == EMBEDDING_DIMENSIONS for embedding in embeddings)


def test_legal_framework_ingestion_updates_embedding_when_document_is_reindexed():
    db = DummyDB()
    updated_content = {**VALID_DOCUMENT, "content": "Updated legal framework content."}

    asyncio.run(ingest_legal_framework_documents(db, [VALID_DOCUMENT]))
    original_embedding = db.added[0].embedding

    db.added = []
    db.existing_document = _as_existing(VALID_DOCUMENT, original_embedding)
    asyncio.run(ingest_legal_framework_documents(db, [updated_content]))

    assert db.existing_document.content == "Updated legal framework content."
    assert db.existing_document.embedding != original_embedding


class _ExistingDocument:
    def __init__(self, source_url, content, embedding):
        self.source_url = source_url
        self.content = content
        self.embedding = embedding
        self.title = ""
        self.document_type = ""
        self.version_label = ""
        self.indexed = False
        self.indexing_errors = []


def _as_existing(candidate, embedding):
    return _ExistingDocument(candidate["source_url"], candidate["content"], embedding)
