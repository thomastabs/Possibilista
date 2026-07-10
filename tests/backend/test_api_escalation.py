from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api import router as api_router


def _make_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    return TestClient(app)


def test_confirmation_notification_returns_true_for_critical_question():
    client = _make_test_client()

    response = client.get(
        "/api/v1/escalation/confirmation-notification",
        headers={"Authorization": "Bearer token"},
        params={"question": "I want to request an exception for a special case equivalence."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["requires_confirmation"] is True
    assert "confirmation" in payload["message"].lower()


def test_confirmation_notification_returns_true_for_out_of_scope_question():
    client = _make_test_client()

    response = client.get(
        "/api/v1/escalation/confirmation-notification",
        headers={"Authorization": "Bearer token"},
        params={"question": "What is the weather tomorrow?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["requires_confirmation"] is True
    assert "confirmation" in payload["message"].lower()


def test_confirmation_notification_returns_false_for_a_normal_question():
    client = _make_test_client()

    response = client.get(
        "/api/v1/escalation/confirmation-notification",
        headers={"Authorization": "Bearer token"},
        params={"question": "What are the professional tracks?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["requires_confirmation"] is False
    assert payload["message"] == "No confirmation needed."


def test_confirmation_notification_requires_bearer_authentication():
    client = _make_test_client()

    response = client.get(
        "/api/v1/escalation/confirmation-notification",
        params={"question": "What are the professional tracks?"},
    )

    assert response.status_code in (401, 403)


def test_confirmation_notification_returns_422_without_question_param():
    client = _make_test_client()

    response = client.get(
        "/api/v1/escalation/confirmation-notification",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 422
