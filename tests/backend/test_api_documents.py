from fastapi import FastAPI
from fastapi.testclient import TestClient

import backend.api.documents as documents_module
from backend.api import router as api_router
from backend.api.documents import get_db_session


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


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_index_legal_framework_endpoint_returns_success_status():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/documents/index-legal-framework",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "Indexed" in payload["message"]


def test_index_legal_framework_endpoint_returns_failure_status_for_corrupted_documents(
    monkeypatch,
):
    async def fake_ingest(db):
        return {"indexed_count": 1, "errors": ["corrupted-doc: Missing or empty required field 'title'."]}

    monkeypatch.setattr(documents_module, "ingest_legal_framework_documents", fake_ingest)
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/documents/index-legal-framework",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"
    assert "corrupted-doc" in payload["message"]


def test_index_legal_framework_endpoint_reports_failure_on_unexpected_exception(monkeypatch):
    async def failing_ingest(db):
        raise RuntimeError("boom")

    monkeypatch.setattr(documents_module, "ingest_legal_framework_documents", failing_ingest)
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/documents/index-legal-framework",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"


def test_index_legal_framework_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.post("/api/v1/documents/index-legal-framework")

    assert response.status_code in (401, 403)
