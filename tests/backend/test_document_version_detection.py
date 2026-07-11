import asyncio
from types import SimpleNamespace

from sqlalchemy.exc import SQLAlchemyError

from backend.services.document_ingestion_service import get_latest_known_document_versions
from backend.services.indexing_status_service import detect_updated_documents


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, documents=None):
        self.documents = documents or []

    async def execute(self, statement):
        return DummyResult(self.documents)


class FailingDB:
    async def execute(self, statement):
        raise SQLAlchemyError("boom")


def _document(source_url, version_label):
    return SimpleNamespace(source_url=source_url, version_label=version_label)


def test_get_latest_known_document_versions_covers_all_four_document_types():
    versions = get_latest_known_document_versions()

    assert set(versions.keys()) == {
        "legal_framework",
        "exam_guide",
        "secondary_track_definitions",
        "higher_ed_requirements",
    }
    assert all(versions[document_type] for document_type in versions)


def test_detect_updated_documents_true_when_no_documents_are_indexed():
    db = DummyDB(documents=[])

    updates_available, outdated = asyncio.run(detect_updated_documents(db))

    assert updates_available is True
    assert len(outdated) > 0


def test_detect_updated_documents_false_when_all_documents_match_latest_versions():
    latest_versions = get_latest_known_document_versions()
    documents = [
        _document(source_url, version_label)
        for catalog in latest_versions.values()
        for source_url, version_label in catalog.items()
    ]
    db = DummyDB(documents=documents)

    updates_available, outdated = asyncio.run(detect_updated_documents(db))

    assert updates_available is False
    assert outdated == []


def test_detect_updated_documents_true_when_a_stored_version_is_outdated():
    latest_versions = get_latest_known_document_versions()
    documents = [
        _document(source_url, version_label)
        for catalog in latest_versions.values()
        for source_url, version_label in catalog.items()
    ]
    documents[0].version_label = "2000-outdated"
    db = DummyDB(documents=documents)

    updates_available, outdated = asyncio.run(detect_updated_documents(db))

    assert updates_available is True
    assert documents[0].source_url in outdated


def test_detect_updated_documents_degrades_gracefully_on_database_error():
    db = FailingDB()

    updates_available, outdated = asyncio.run(detect_updated_documents(db))

    assert updates_available is False
    assert outdated == []
