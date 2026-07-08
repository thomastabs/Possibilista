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
    def __init__(self, session=None, previous_message=None, fail=False):
        self.session = session
        self.previous_message = previous_message
        self.fail = fail
        self.added = []
        self.committed = False
        self.rolled_back = False

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
        entity = statement.column_descriptions[0]["entity"]
        if getattr(entity, "__name__", "") == "ChatMessage":
            return DummyResult(self.previous_message)
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
    assert "https://www.dge.mec.pt/" in response["answer"]
    assert all("https://www.dge.mec.pt/" in fact for fact in response["facts"])


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
    assert "cannot answer this question based on the current official sources" in (
        response["answer"].lower()
    )


def test_post_chat_message_persists_insufficient_info_flag_in_database():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=10)
    db = DummyDB(session=session)

    response = asyncio.run(
        post_chat_message(
            payload=type(
                "Payload", (), {"message": "What is the weather tomorrow?", "session_id": str(session_id)}
            )(),
            _credentials=object(),
            db=db,
        )
    )

    assert response.insufficient_info is True
    assert len(db.added) == 1
    assert db.added[0].insufficient_info is True


def test_build_chat_response_rejects_empty_message():
    try:
        build_chat_response("   ", "session-4")
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for an empty message.")


def test_build_chat_response_flags_confirmation_for_special_case_question():
    response = build_chat_response(
        "My situation is a special case — can I get an exception to enroll?",
        "session-5",
    )

    assert response["requires_confirmation"] is True


def test_post_chat_message_persists_requires_confirmation_flag_in_database():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=10)
    db = DummyDB(session=session)

    response = asyncio.run(
        post_chat_message(
            payload=type(
                "Payload",
                (),
                {
                    "message": "I want to request an exception for a special case equivalence.",
                    "session_id": str(session_id),
                },
            )(),
            _credentials=object(),
            db=db,
        )
    )

    assert response.requires_confirmation is True
    assert len(db.added) == 1
    assert db.added[0].requires_confirmation is True


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
    assert all("https://www.dge.mec.pt/" in fact for fact in payload["facts"])


def test_post_chat_message_endpoint_flags_are_false_when_not_applicable():
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


def test_post_chat_message_endpoint_marks_interpretation_answers_distinctly():
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
    assert "interpretation" in payload["answer"].lower()
    assert "not a direct quote from official sources" in payload["answer"].lower()


def test_post_chat_message_endpoint_breaks_down_a_compound_question_into_parts():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={
            "message": (
                "What are the professional tracks? "
                "What are the specialized artistic tracks?"
            ),
            "session_id": str(session_id),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"].startswith("1) ")
    assert "2) " in payload["answer"]
    assert any("Professional Courses Guidance" in fact for fact in payload["facts"])
    assert any("Specialized Artistic Courses Guidance" in fact for fact in payload["facts"])
    assert payload["insufficient_info"] is False


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


def test_post_chat_message_endpoint_retains_context_for_related_follow_up():
    from types import SimpleNamespace

    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    previous_message = SimpleNamespace(
        id=uuid4(),
        context_tokens=["Professional Courses Guidance"],
        facts=["Professional Courses Guidance (https://www.dge.mec.pt/cursos-profissionais): ..."],
    )
    client = _make_test_client(DummyDB(session=session, previous_message=previous_message))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={"message": "What subjects does it include?", "session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["insufficient_info"] is False
    assert payload["facts"] == previous_message.facts
    assert "continuing from the previous topic" in payload["answer"].lower()


def test_post_chat_message_endpoint_rejects_missing_session_id():
    client = _make_test_client(DummyDB(session=None))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={"message": "What are the professional tracks?"},
    )

    assert response.status_code == 422


def test_post_chat_message_endpoint_rejects_empty_message():
    client = _make_test_client(DummyDB(session=None))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={"message": "", "session_id": str(uuid4())},
    )

    assert response.status_code == 422


class StatefulDummyDB:
    """Chains each persisted ChatMessage as the "previous" one for the next query,
    simulating a real multi-turn conversation across sequential requests."""

    def __init__(self, session):
        self.session = session
        self.added = []

    async def execute(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        if getattr(entity, "__name__", "") == "ChatMessage":
            return DummyResult(self.added[-1] if self.added else None)
        return DummyResult(self.session)

    def add(self, record):
        self.added.append(record)

    async def commit(self):
        pass

    async def rollback(self):
        pass


def test_post_chat_message_endpoint_multi_turn_conversation_stays_coherent():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(StatefulDummyDB(session=session))

    first = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={"message": "What are the professional tracks?", "session_id": str(session_id)},
    )
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["facts"]
    assert first_payload["insufficient_info"] is False

    second = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={"message": "What subjects does it include?", "session_id": str(session_id)},
    )
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["insufficient_info"] is False
    assert second_payload["facts"] == first_payload["facts"]
    assert "continuing from the previous topic" in second_payload["answer"].lower()

    third = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={
            "message": "What are the specialized artistic tracks?",
            "session_id": str(session_id),
        },
    )
    assert third.status_code == 200
    third_payload = third.json()
    assert third_payload["facts"] != first_payload["facts"]
    assert "artistic" in third_payload["answer"].lower()


def test_post_chat_message_endpoint_resets_context_on_topic_change():
    from types import SimpleNamespace

    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    previous_message = SimpleNamespace(
        id=uuid4(),
        context_tokens=["Professional Courses Guidance"],
        facts=["Professional Courses Guidance (https://www.dge.mec.pt/cursos-profissionais): ..."],
    )
    client = _make_test_client(DummyDB(session=session, previous_message=previous_message))

    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer token"},
        json={
            "message": "What are the specialized artistic tracks?",
            "session_id": str(session_id),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["facts"] != previous_message.facts
    assert "artistic" in payload["answer"].lower()
