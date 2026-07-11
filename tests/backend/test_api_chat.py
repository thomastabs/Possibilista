from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

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


def test_post_chat_message_endpoint_flags_requires_confirmation_for_critical_question():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={
            "message": "I want to request an exception for a special case equivalence.",
            "session_id": str(session_id),
        },
    )

    assert response.status_code == 200
    assert response.json()["requires_confirmation"] is True


def test_post_chat_message_endpoint_flags_requires_confirmation_when_no_grounded_answer():
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


def test_post_chat_message_endpoint_withholds_definitive_answer_for_critical_decision():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={
            "message": "I want to enroll in the professional track.",
            "session_id": str(session_id),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["requires_confirmation"] is True
    assert payload["insufficient_info"] is True
    assert payload["facts"] == []
    assert payload["interpretations"] == []
    assert payload["confirmation_advice"]
    assert (
        "human" in payload["confirmation_advice"].lower()
        or "institution" in payload["confirmation_advice"].lower()
    )


def test_post_chat_message_endpoint_does_not_flag_confirmation_for_a_grounded_question():
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
    assert payload["insufficient_info"] is False
    assert payload["requires_confirmation"] is False
