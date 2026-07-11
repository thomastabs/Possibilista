"""Integration tests for POST /api/v1/documents/index-update (Story 9389391).

Unlike test_api_documents.py's index-update tests (which mock detect_updated_documents/
reindex_all_official_documents to isolate the endpoint's status/message mapping), these run
the real version-detection and reindexing logic end-to-end against a stateful in-memory
Document store, verifying actual database state changes for both the refresh and retention
scenarios.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api import router as api_router
from backend.api.documents import get_db_session
from backend.models.document import Document
from backend.services.document_ingestion_service import get_latest_known_document_versions


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalar_one_or_none(self):
        return self._records

    def scalars(self):
        return self

    def all(self):
        return self._records


class StatefulDocumentDB:
    """Tracks persisted Document rows across calls in a plain list, supporting both a
    whole-table scan (select(Document), used by version detection) and a lookup by
    source_url (select(Document).where(Document.source_url == ...), used by the ingestion
    pipelines' upsert) against the same backing store."""

    def __init__(self, documents=None):
        self.documents: list[Document] = list(documents or [])
        self.committed = 0

    async def execute(self, statement):
        source_url = self._extract_source_url_filter(statement)
        if source_url is not None:
            match = next(
                (document for document in self.documents if document.source_url == source_url),
                None,
            )
            return DummyResult(match)
        return DummyResult(list(self.documents))

    @staticmethod
    def _extract_source_url_filter(statement):
        whereclause = getattr(statement, "whereclause", None)
        if whereclause is None:
            return None
        right = getattr(whereclause, "right", None)
        return getattr(right, "value", None)

    def add(self, record):
        self.documents.append(record)

    async def commit(self):
        self.committed += 1

    async def rollback(self):
        pass


def _make_test_client(db: StatefulDocumentDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_index_update_refreshes_the_index_when_updated_documents_are_available():
    db = StatefulDocumentDB(documents=[])
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/documents/index-update",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["updated"] is True

    latest_versions = get_latest_known_document_versions()
    expected_source_urls = {
        source_url for catalog in latest_versions.values() for source_url in catalog
    }
    stored_source_urls = {document.source_url for document in db.documents}
    assert stored_source_urls == expected_source_urls
    assert all(document.indexed for document in db.documents)


def test_index_update_retains_the_existing_index_when_no_updates_are_available():
    latest_versions = get_latest_known_document_versions()
    existing_documents = [
        Document(
            title=f"Existing document for {source_url}",
            content="Existing content.",
            source_url=source_url,
            document_type=document_type,
            version_label=version_label,
            indexed=True,
            indexing_errors=[],
            embedding=[0.0] * 8,
        )
        for document_type, catalog in latest_versions.items()
        for source_url, version_label in catalog.items()
    ]
    db = StatefulDocumentDB(documents=existing_documents)
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/documents/index-update",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["updated"] is False
    assert "retained" in payload["message"].lower()

    assert len(db.documents) == len(existing_documents)
    assert all(document.content == "Existing content." for document in db.documents)
    assert db.committed == 0
