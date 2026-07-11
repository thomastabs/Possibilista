from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api import router as api_router
from backend.api.family import get_db_session


class DummyResult:
    def __init__(self, record):
        self._record = record

    def scalar_one_or_none(self):
        return self._record


class DummyDB:
    def __init__(self, explanation=None):
        self.explanation = explanation

    async def execute(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        if getattr(entity, "__name__", "") == "Explanation":
            return DummyResult(self.explanation)
        return DummyResult(None)


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_fact_interpretation_distinction_endpoint_returns_facts_and_interpretations():
    explanation_id = uuid4()
    explanation = SimpleNamespace(
        facts=["The professional track leads to a secondary qualification."],
        interpretations=["This may suit a student who prefers hands-on learning."],
        unavailable_info=False,
    )
    client = _make_test_client(DummyDB(explanation=explanation))

    response = client.get(
        "/api/v1/family/fact-interpretation-distinction",
        headers={"Authorization": "Bearer token"},
        params={"explanation_id": str(explanation_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["facts"] == explanation.facts
    assert payload["interpretations"] == explanation.interpretations
    assert payload["unavailable_info"] is False


def test_fact_interpretation_distinction_endpoint_returns_unavailable_for_missing_explanation():
    client = _make_test_client(DummyDB(explanation=None))

    response = client.get(
        "/api/v1/family/fact-interpretation-distinction",
        headers={"Authorization": "Bearer token"},
        params={"explanation_id": str(uuid4())},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["facts"] == []
    assert payload["interpretations"] == []
    assert payload["unavailable_info"] is True


def test_fact_interpretation_distinction_endpoint_returns_400_for_invalid_explanation_id():
    client = _make_test_client(DummyDB(explanation=None))

    response = client.get(
        "/api/v1/family/fact-interpretation-distinction",
        headers={"Authorization": "Bearer token"},
        params={"explanation_id": "not-a-uuid"},
    )

    assert response.status_code == 400


def test_fact_interpretation_distinction_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB(explanation=None))

    response = client.get(
        "/api/v1/family/fact-interpretation-distinction",
        params={"explanation_id": str(uuid4())},
    )

    assert response.status_code in (401, 403)
