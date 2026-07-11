from fastapi import FastAPI
from fastapi.testclient import TestClient

import backend.api.documents as documents_module
from backend.api import router as api_router
from backend.api.documents import get_db_session


class DummyResult:
    def scalar_one_or_none(self):
        return None

    def scalars(self):
        return self

    def all(self):
        return []


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


def test_index_secondary_track_definitions_endpoint_returns_success_status():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/documents/index-secondary-track-definitions",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "Indexed" in payload["message"]


def test_index_secondary_track_definitions_endpoint_returns_failure_for_incomplete_documents(
    monkeypatch,
):
    async def fake_ingest(db):
        return {
            "indexed_count": 0,
            "errors": [
                "incomplete-doc: Incomplete secondary-track definition: missing exam requirements."
            ],
        }

    monkeypatch.setattr(
        documents_module, "ingest_secondary_track_definition_documents", fake_ingest
    )
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/documents/index-secondary-track-definitions",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"
    assert "incomplete-doc" in payload["message"]


def test_index_secondary_track_definitions_endpoint_reports_failure_on_unexpected_exception(
    monkeypatch,
):
    async def failing_ingest(db):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        documents_module, "ingest_secondary_track_definition_documents", failing_ingest
    )
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/documents/index-secondary-track-definitions",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "failed"


def test_index_secondary_track_definitions_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.post("/api/v1/documents/index-secondary-track-definitions")

    assert response.status_code in (401, 403)


def test_indexing_status_endpoint_returns_status_for_all_document_types(monkeypatch):
    async def fake_status(db):
        return {
            "legal_framework_status": "indexed",
            "exam_guide_status": "missing",
            "secondary_track_definitions_status": "missing",
            "higher_ed_requirements_status": "missing",
            "errors": ["exam_guide: document is missing."],
        }

    monkeypatch.setattr(documents_module, "get_indexing_status", fake_status)
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/documents/indexing-status",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["legal_framework_status"] == "indexed"
    assert payload["exam_guide_status"] == "missing"
    assert payload["secondary_track_definitions_status"] == "missing"
    assert payload["higher_ed_requirements_status"] == "missing"
    assert "exam_guide: document is missing." in payload["errors"]


def test_indexing_status_endpoint_reports_missing_exam_guide_alert(monkeypatch):
    async def fake_status(db):
        return {
            "legal_framework_status": "indexed",
            "exam_guide_status": "missing",
            "secondary_track_definitions_status": "missing",
            "higher_ed_requirements_status": "missing",
            "errors": ["exam_guide: document is missing."],
        }

    monkeypatch.setattr(documents_module, "get_indexing_status", fake_status)
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/documents/indexing-status",
        headers={"Authorization": "Bearer token"},
    )

    payload = response.json()
    assert payload["exam_guide_status"] == "missing"
    assert any("exam_guide" in error for error in payload["errors"])


def test_indexing_status_endpoint_reports_all_types_missing_with_no_documents():
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/documents/indexing-status",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["legal_framework_status"] == "missing"
    assert payload["exam_guide_status"] == "missing"
    assert payload["secondary_track_definitions_status"] == "missing"
    assert payload["higher_ed_requirements_status"] == "missing"
    assert len(payload["errors"]) == 4


def test_indexing_status_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.get("/api/v1/documents/indexing-status")

    assert response.status_code in (401, 403)


def test_index_higher_ed_requirements_endpoint_returns_success_status():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/documents/index-higher-ed-requirements",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "Indexed" in payload["message"]


def test_index_higher_ed_requirements_endpoint_returns_failure_for_outdated_documents(
    monkeypatch,
):
    async def fake_ingest(db):
        return {
            "indexed_count": 0,
            "errors": [
                "outdated-doc: Outdated version '2019-edition'; requires a version from "
                "2026 or later."
            ],
        }

    monkeypatch.setattr(documents_module, "ingest_higher_ed_requirements_documents", fake_ingest)
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/documents/index-higher-ed-requirements",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"
    assert "outdated-doc" in payload["message"]
    assert "updated versions" in payload["message"]


def test_index_higher_ed_requirements_endpoint_reports_failure_on_unexpected_exception(
    monkeypatch,
):
    async def failing_ingest(db):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        documents_module, "ingest_higher_ed_requirements_documents", failing_ingest
    )
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/documents/index-higher-ed-requirements",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "failed"


def test_index_higher_ed_requirements_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.post("/api/v1/documents/index-higher-ed-requirements")

    assert response.status_code in (401, 403)


def test_documents_retrieve_endpoint_returns_matching_documents(monkeypatch):
    async def fake_retrieve(db, query, limit=3):
        return {
            "documents": [
                {
                    "title": "Professional Courses Guidance",
                    "content": "Professional courses combine general education with technical training.",
                    "source_url": "https://www.dge.mec.pt/cursos-profissionais",
                }
            ],
            "no_source": False,
        }

    monkeypatch.setattr(documents_module, "retrieve_relevant_documents", fake_retrieve)
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/documents/retrieve",
        headers={"Authorization": "Bearer token"},
        params={"query": "What are professional courses?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["no_source"] is False
    assert payload["documents"][0]["title"] == "Professional Courses Guidance"


def test_documents_retrieve_endpoint_returns_no_source_when_nothing_matches(monkeypatch):
    async def fake_retrieve(db, query, limit=3):
        return {"documents": [], "no_source": True}

    monkeypatch.setattr(documents_module, "retrieve_relevant_documents", fake_retrieve)
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/documents/retrieve",
        headers={"Authorization": "Bearer token"},
        params={"query": "What is the weather tomorrow?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["no_source"] is True
    assert payload["documents"] == []


def test_documents_retrieve_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.get("/api/v1/documents/retrieve", params={"query": "test"})

    assert response.status_code in (401, 403)


def test_documents_retrieve_endpoint_requires_query_param():
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/documents/retrieve",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 422
