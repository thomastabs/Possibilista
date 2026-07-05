import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api import router as api_router
from backend.services.natural_language_question import answer_natural_language_question


def test_answer_natural_language_question_clear_question():
    response = asyncio.run(
        answer_natural_language_question(
            "What are the available secondary tracks?",
            "session-1",
        )
    )

    assert response["session_id"] == "session-1"
    assert response["clarification_needed"] is False
    assert response["out_of_scope"] is False
    assert response["clarification_options"] == []
    assert "official secondary education guidance" in response["answer"].lower()
    assert response["suggestion"] == ""
    assert response["documents"]
    assert response["no_source"] is False


def test_answer_natural_language_question_ambiguous_question():
    response = asyncio.run(
        answer_natural_language_question(
            "Tell me about secondary education.",
            "session-2",
        )
    )

    assert response["session_id"] == "session-2"
    assert response["clarification_needed"] is True
    assert response["out_of_scope"] is False
    assert response["clarification_options"]
    assert "official secondary education guidance" in response["answer"].lower()


def test_answer_natural_language_question_out_of_scope_question():
    response = asyncio.run(
        answer_natural_language_question(
            "What is the weather tomorrow?",
            "session-3",
        )
    )

    assert response["session_id"] == "session-3"
    assert response["clarification_needed"] is False
    assert response["out_of_scope"] is True
    assert response["clarification_options"] == []
    assert "human advisor" in response["suggestion"].lower()
    assert response["documents"] == []
    assert response["no_source"] is True


def test_answer_natural_language_question_marks_no_source_when_documents_missing():
    async def empty_retriever(_question: str):
        return []

    response = asyncio.run(
        answer_natural_language_question(
            "What are the available secondary tracks?",
            "session-4",
            document_retriever=empty_retriever,
        )
    )

    assert response["no_source"] is True
    assert response["documents"] == []
    assert "could not find an official document" in response["answer"].lower()


def test_answer_natural_language_question_rejects_empty_question():
    try:
        asyncio.run(answer_natural_language_question("   ", "session-4"))
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for an empty question.")


def _make_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    return TestClient(app)


def test_post_natural_language_question_endpoint_returns_clear_answer():
    client = _make_test_client()

    response = client.post(
        "/api/v1/chat/natural-language-question",
        headers={"Authorization": "Bearer token"},
        json={
            "question": "What are the available secondary tracks?",
            "session_id": "session-1",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == "session-1"
    assert payload["clarification_needed"] is False
    assert payload["out_of_scope"] is False
    assert "official secondary education guidance" in payload["answer"].lower()
    assert payload["documents"]
    assert payload["no_source"] is False


def test_post_natural_language_question_endpoint_returns_clarification_options():
    client = _make_test_client()

    response = client.post(
        "/api/v1/chat/natural-language-question",
        headers={"Authorization": "Bearer token"},
        json={
            "question": "Tell me about secondary education.",
            "session_id": "session-2",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["clarification_needed"] is True
    assert payload["clarification_options"]
    assert payload["out_of_scope"] is False


def test_post_natural_language_question_endpoint_returns_out_of_scope_message():
    client = _make_test_client()

    response = client.post(
        "/api/v1/chat/natural-language-question",
        headers={"Authorization": "Bearer token"},
        json={
            "question": "What is the weather tomorrow?",
            "session_id": "session-3",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["out_of_scope"] is True
    assert "human advisor" in payload["suggestion"].lower()


def test_post_natural_language_question_endpoint_requires_bearer_authentication():
    client = _make_test_client()

    response = client.post(
        "/api/v1/chat/natural-language-question",
        json={
            "question": "What are the available secondary tracks?",
            "session_id": "session-4",
        },
    )

    assert response.status_code == 403


def test_post_natural_language_question_endpoint_validates_payload_shape():
    client = _make_test_client()

    response = client.post(
        "/api/v1/chat/natural-language-question",
        headers={"Authorization": "Bearer token"},
        json={"session_id": "session-5"},
    )

    assert response.status_code == 422
