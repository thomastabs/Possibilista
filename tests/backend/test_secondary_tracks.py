from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.secondary_tracks import get_db_session
from backend.models.secondary_track import SecondaryTrack


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, tracks=None, fail=False):
        self.tracks = tracks or []
        self.fail = fail

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
        return DummyResult(self.tracks)


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_get_all_secondary_tracks():
    tracks = [
        SecondaryTrack(id=uuid4(), name="Science and Technology", description="STEM focused track."),
        SecondaryTrack(id=uuid4(), name="Languages and Humanities", description=None),
    ]
    client = _make_test_client(DummyDB(tracks=tracks))

    response = client.get("/api/v1/secondary-tracks")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "tracks": [
            {"id": str(tracks[0].id), "name": "Science and Technology", "description": "STEM focused track."},
            {"id": str(tracks[1].id), "name": "Languages and Humanities", "description": None},
        ]
    }


def test_get_secondary_tracks_requires_no_authentication():
    client = _make_test_client(DummyDB(tracks=[]))

    response = client.get("/api/v1/secondary-tracks")

    assert response.status_code == 200


def test_get_secondary_tracks_returns_500_on_database_failure():
    client = _make_test_client(DummyDB(fail=True))

    response = client.get("/api/v1/secondary-tracks")

    assert response.status_code == 500
