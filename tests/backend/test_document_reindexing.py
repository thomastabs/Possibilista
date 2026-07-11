import asyncio

from backend.services.document_ingestion_service import reindex_all_official_documents


class DummyResult:
    def scalar_one_or_none(self):
        return None


class DummyDB:
    def __init__(self):
        self.added = []
        self.committed = 0

    async def execute(self, statement):
        return DummyResult()

    def add(self, record):
        self.added.append(record)

    async def commit(self):
        self.committed += 1

    async def rollback(self):
        pass


def test_reindex_all_official_documents_indexes_every_document_type():
    db = DummyDB()

    result = asyncio.run(reindex_all_official_documents(db))

    assert result["errors"] == []
    # 2 legal framework + 1 exam guide + 1 secondary track definitions + 1 higher-ed requirements
    assert result["indexed_count"] == 5
    document_types = {document.document_type for document in db.added}
    assert document_types == {
        "legal_framework",
        "exam_guide",
        "secondary_track_definitions",
        "higher_ed_requirements",
    }


def test_reindex_all_official_documents_persists_all_indexed_documents():
    db = DummyDB()

    asyncio.run(reindex_all_official_documents(db))

    assert len(db.added) == 5
    assert all(document.indexed for document in db.added)
    assert all(document.embedding is not None for document in db.added)
