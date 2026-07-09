from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.secondary_tracks import get_db_session
from backend.models.secondary_track import SecondaryTrackDisciplineCombination


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def one_or_none(self):
        return self._records[0] if self._records else None


class DummyDB:
    def __init__(self, discipline_combination=None, fail=False):
        self.discipline_combination = discipline_combination
        self.fail = fail

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
        records = [self.discipline_combination] if self.discipline_combination else []
        return DummyResult(records)


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_discipline_combinations_endpoint_returns_valid_track_combinations():
    track_id = uuid4()
    combination = SecondaryTrackDisciplineCombination(
        id=uuid4(),
        track_id=track_id,
        trienais=["Mathematics A"],
        bienais=["Biology"],
        anuais=["Philosophy"],
        combinations=["Mathematics A + Biology"],
        message="",
    )
    client = _make_test_client(DummyDB(discipline_combination=combination))

    response = client.get(f"/api/v1/secondary-tracks/{track_id}/discipline-combinations")

    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "trienais": ["Mathematics A"],
        "bienais": ["Biology"],
        "anuais": ["Philosophy"],
        "combinations": ["Mathematics A + Biology"],
        "message": "",
    }


def test_discipline_combinations_endpoint_returns_invalid_when_no_combinations_exist():
    client = _make_test_client(DummyDB())

    response = client.get(f"/api/v1/secondary-tracks/{uuid4()}/discipline-combinations")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert payload["trienais"] == []
    assert payload["bienais"] == []
    assert payload["anuais"] == []
    assert payload["combinations"] == []
    assert "no valid discipline combinations" in payload["message"].lower()


def test_discipline_combinations_endpoint_rejects_malformed_track_id():
    client = _make_test_client(DummyDB())

    response = client.get("/api/v1/secondary-tracks/not-a-uuid/discipline-combinations")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert "invalid" in payload["message"].lower()


def test_discipline_combinations_endpoint_returns_500_on_database_failure():
    client = _make_test_client(DummyDB(fail=True))

    response = client.get(f"/api/v1/secondary-tracks/{uuid4()}/discipline-combinations")

    assert response.status_code == 500
