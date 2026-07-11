from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api import router as api_router
from backend.api.chat import get_db_session
from backend.models.student_session import StudentSession


class DummyResult:
    def __init__(self, record):
        self._record = record

    def scalar_one_or_none(self):
        return self._record


class DummyDB:
    def __init__(self, session=None):
        self.session = session
        self.added = []
        self.committed = False

    async def execute(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        if getattr(entity, "__name__", "") == "ChatMessage":
            return DummyResult(None)
        return DummyResult(self.session)

    def add(self, record):
        self.added.append(record)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_chat_message_classification_separates_facts_and_interpretations():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={"message": "What are the professional tracks?", "session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["facts"]
    assert payload["interpretations"] == []
    assert payload["is_fact"] is True
    assert payload["is_interpretation"] is False


def test_official_document_references_included_for_grounded_answers():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={"message": "What are the professional tracks?", "session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["documents"]
    for document in payload["documents"]:
        assert set(document) == {"title", "content", "source_url"}


def test_official_document_references_empty_for_insufficient_info():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={"message": "What is the weather tomorrow?", "session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["insufficient_info"] is True
    assert payload["requires_confirmation"] is True
    assert payload["documents"] == []


def test_chat_message_classification_flags_interpretative_answers_for_confirmation():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={
            "message": "Which professional track would you recommend for me?",
            "session_id": str(session_id),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["interpretations"]
    assert payload["is_interpretation"] is True
    assert payload["requires_confirmation"] is True
