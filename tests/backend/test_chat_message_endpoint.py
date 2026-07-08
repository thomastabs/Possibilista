import asyncio
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.chat import get_db_session, post_chat_message, resolve_student_session
from backend.models.student_session import StudentSession
from backend.services.chat_service import build_chat_response


class DummyResult:
    def __init__(self, record):
        self._record = record

    def scalar_one_or_none(self):
        return self._record


class DummyDB:
    def __init__(self, session=None, fail=False):
        self.session = session
        self.fail = fail
        self.added = []
        self.committed = False
        self.rolled_back = False

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
        return DummyResult(self.session)

    def add(self, record):
        self.added.append(record)

    async def commit(self):
        if self.fail:
            raise SQLAlchemyError("boom")
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def test_build_chat_response_cites_official_documents_for_factual_question():
    response = build_chat_response(
        "What are the professional secondary tracks?",
        "session-1",
    )

    assert response["session_id"] == "session-1"
    assert response["facts"]
    assert response["interpretations"] == []
    assert response["insufficient_info"] is False
    assert "according to the official documents" in response["answer"].lower()


def test_build_chat_response_marks_interpretation_for_advice_question():
    response = build_chat_response(
        "Which professional track would you recommend for me?",
        "session-2",
    )

    assert response["interpretations"]
    assert "interpretation" in response["answer"].lower()
    assert "not a direct quote from official sources" in response["answer"].lower()


def test_build_chat_response_flags_insufficient_info_when_no_match():
    response = build_chat_response("What is the weather tomorrow?", "session-3")

    assert response["insufficient_info"] is True
    assert response["facts"] == []
    assert response["interpretations"] == []


def test_build_chat_response_rejects_empty_message():
    try:
        build_chat_response("   ", "session-4")
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for an empty message.")


def test_resolve_student_session_rejects_unknown_session():
    db = DummyDB(session=None)

    try:
        asyncio.run(resolve_student_session(db, str(uuid4())))
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Expected HTTPException for unknown session.")


def test_resolve_student_session_rejects_malformed_session_id():
    db = DummyDB(session=None)

    try:
        asyncio.run(resolve_student_session(db, "not-a-uuid"))
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Expected HTTPException for malformed session id.")


def test_post_chat_message_persists_and_returns_response():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=10)
    db = DummyDB(session=session)

    response = asyncio.run(
        post_chat_message(
            payload=type(
                "Payload", (), {"message": "What are the professional tracks?", "session_id": str(session_id)}
            )(),
            _credentials=object(),
            db=db,
        )
    )

    assert response.session_id == str(session_id)
    assert response.facts
    assert db.committed is True
    assert len(db.added) == 1
    assert db.added[0].message == "What are the professional tracks?"


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_post_chat_message_endpoint_returns_200_with_full_shape():
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
    assert set(payload) == {
        "answer",
        "facts",
        "interpretations",
        "insufficient_info",
        "requires_confirmation",
        "session_id",
    }
    assert payload["session_id"] == str(session_id)
    assert payload["facts"]


def test_post_chat_message_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB(session=None))

    response = client.post(
        "/api/v1/chat/message",
        json={"message": "What are the professional tracks?", "session_id": str(uuid4())},
    )

    assert response.status_code in (401, 403)


def test_post_chat_message_endpoint_returns_401_for_unknown_session():
    client = _make_test_client(DummyDB(session=None))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={"message": "What are the professional tracks?", "session_id": str(uuid4())},
    )

    assert response.status_code == 401
