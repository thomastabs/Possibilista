import asyncio
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.secondary_tracks import get_db_session
from backend.models.secondary_track import (
    SecondaryTrack,
    SecondaryTrackDiscipline,
    SecondaryTrackExamRequirement,
)
from backend.services.secondary_track_service import get_disciplines_for_track


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, tracks=None, fail=False, track_by_id=None, disciplines=None, exam_requirements=None):
        self.tracks = tracks or []
        self.fail = fail
        self.track_by_id = track_by_id or {}
        self.disciplines = disciplines or []
        self.exam_requirements = exam_requirements or []

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
        entity = statement.column_descriptions[0]["entity"]
        entity_name = getattr(entity, "__name__", "")
        if entity_name == "SecondaryTrackDiscipline":
            return DummyResult(self.disciplines)
        if entity_name == "SecondaryTrackExamRequirement":
            return DummyResult(self.exam_requirements)
        return DummyResult(self.tracks)

    async def get(self, model, record_id):
        if self.fail:
            raise SQLAlchemyError("boom")
        return self.track_by_id.get(record_id)


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


def test_get_disciplines_endpoint_returns_valid_track_disciplines():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description="STEM focused track.")
    disciplines = [
        SecondaryTrackDiscipline(id=uuid4(), track_id=track_id, discipline_name="Mathematics"),
        SecondaryTrackDiscipline(id=uuid4(), track_id=track_id, discipline_name="Physics"),
    ]
    client = _make_test_client(DummyDB(track_by_id={track_id: track}, disciplines=disciplines))

    response = client.get(f"/api/v1/secondary-tracks/{track_id}/disciplines")

    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "disciplines": ["Mathematics", "Physics"],
        "message": "Disciplines retrieved successfully.",
    }


def test_get_disciplines_endpoint_returns_invalid_for_unknown_track():
    client = _make_test_client(DummyDB())

    response = client.get(f"/api/v1/secondary-tracks/{uuid4()}/disciplines")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert payload["disciplines"] == []
    assert payload["message"]


def test_get_disciplines_endpoint_rejects_malformed_track_id():
    client = _make_test_client(DummyDB())

    response = client.get("/api/v1/secondary-tracks/not-a-uuid/disciplines")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert payload["disciplines"] == []
    assert "invalid" in payload["message"].lower()


def test_get_disciplines_for_track_returns_disciplines_for_valid_track():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description="STEM focused track.")
    disciplines = [
        SecondaryTrackDiscipline(id=uuid4(), track_id=track_id, discipline_name="Mathematics"),
        SecondaryTrackDiscipline(id=uuid4(), track_id=track_id, discipline_name="Physics"),
    ]
    db = DummyDB(track_by_id={track_id: track}, disciplines=disciplines)

    result = asyncio.run(get_disciplines_for_track(db, str(track_id)))

    assert result == {
        "valid": True,
        "disciplines": ["Mathematics", "Physics"],
        "message": "Disciplines retrieved successfully.",
    }


def test_get_disciplines_for_track_returns_invalid_for_unknown_track():
    db = DummyDB()

    result = asyncio.run(get_disciplines_for_track(db, str(uuid4())))

    assert result["valid"] is False
    assert result["disciplines"] == []
    assert result["message"] == "The specified secondary track does not exist. Please ask about valid tracks."


def test_get_disciplines_for_track_returns_invalid_for_malformed_id():
    db = DummyDB()

    result = asyncio.run(get_disciplines_for_track(db, "not-a-uuid"))

    assert result == {
        "valid": False,
        "disciplines": [],
        "message": "Invalid track ID format.",
    }


def test_exam_requirements_endpoint_returns_valid_track_exams():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description="STEM focused track.")
    exam_requirements = [
        SecondaryTrackExamRequirement(
            id=uuid4(), track_id=track_id, exam_name="Mathematics A", timing="End of 12th grade"
        ),
        SecondaryTrackExamRequirement(
            id=uuid4(), track_id=track_id, exam_name="Physics and Chemistry", timing="End of 11th grade"
        ),
    ]
    client = _make_test_client(DummyDB(track_by_id={track_id: track}, exam_requirements=exam_requirements))

    response = client.get(f"/api/v1/secondary-tracks/{track_id}/exam-requirements")

    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "exams": [
            {"name": "Mathematics A", "timing": "End of 12th grade"},
            {"name": "Physics and Chemistry", "timing": "End of 11th grade"},
        ],
        "message": "Exam requirements retrieved successfully.",
    }


def test_exam_requirements_endpoint_returns_invalid_for_unknown_track():
    client = _make_test_client(DummyDB())

    response = client.get(f"/api/v1/secondary-tracks/{uuid4()}/exam-requirements")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert payload["exams"] == []
    assert "no information is available" in payload["message"].lower()


def test_exam_requirements_endpoint_rejects_malformed_track_id():
    client = _make_test_client(DummyDB())

    response = client.get("/api/v1/secondary-tracks/not-a-uuid/exam-requirements")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert payload["exams"] == []
    assert "invalid" in payload["message"].lower()
