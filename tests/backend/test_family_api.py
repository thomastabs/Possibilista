from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api import router as api_router
from backend.api.family import get_db_session
from backend.models.student_session import StudentSession


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def scalar_one_or_none(self):
        return self._records

    def unique(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(
        self, session=None, interests=None, motivation=None, strengths=None, tracks=None
    ):
        self.session = session
        self.interests = interests or []
        self.motivation = motivation
        self.strengths = strengths
        self.tracks = tracks or []

    async def execute(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        name = getattr(entity, "__name__", "")
        if name == "StudentSession":
            return DummyResult(self.session)
        if name == "StudentInterest":
            return DummyResult(self.interests)
        if name == "StudentMotivation":
            return DummyResult(self.motivation)
        if name == "StudentStrengthWeakness":
            return DummyResult(self.strengths)
        if name == "SecondaryTrack":
            return DummyResult(self.tracks)
        return DummyResult([])


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_exploration_path_returns_explanations_when_data_is_present():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    db = DummyDB(
        session=session,
        interests=[SimpleNamespace(interest="Robotics", skipped=False)],
        motivation=SimpleNamespace(motivations="Wants to help people.", declined=False),
        strengths=SimpleNamespace(strengths=["Math"], weaknesses=["History"], partial=False),
    )
    client = _make_test_client(db)

    response = client.get(
        "/api/v1/family/exploration-path",
        headers={"Authorization": "Bearer token"},
        params={"student_session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["no_data"] is False
    assert "Robotics" in payload["interests_explanation"]
    assert "help people" in payload["motivations_explanation"]
    assert "Math" in payload["academic_areas_explanation"]


def test_exploration_path_returns_no_data_message_when_nothing_recorded():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.get(
        "/api/v1/family/exploration-path",
        headers={"Authorization": "Bearer token"},
        params={"student_session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["no_data"] is True
    assert "not started exploring" in payload["interests_explanation"].lower()
    assert "not started exploring" in payload["motivations_explanation"].lower()
    assert "not started exploring" in payload["academic_areas_explanation"].lower()


def test_exploration_path_requires_bearer_authentication():
    client = _make_test_client(DummyDB(session=None))

    response = client.get(
        "/api/v1/family/exploration-path",
        params={"student_session_id": str(uuid4())},
    )

    assert response.status_code in (401, 403)


def test_exploration_path_returns_404_for_unknown_student_session():
    client = _make_test_client(DummyDB(session=None))

    response = client.get(
        "/api/v1/family/exploration-path",
        headers={"Authorization": "Bearer token"},
        params={"student_session_id": str(uuid4())},
    )

    assert response.status_code == 404


def test_exploration_path_returns_404_for_malformed_student_session_id():
    client = _make_test_client(DummyDB(session=None))

    response = client.get(
        "/api/v1/family/exploration-path",
        headers={"Authorization": "Bearer token"},
        params={"student_session_id": "not-a-uuid"},
    )

    assert response.status_code == 404


def test_guidance_outcomes_returns_recommendations_with_text_and_source():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    track = SimpleNamespace(
        name="Professional Track",
        description="Combines general education with technical training.",
        disciplines=[SimpleNamespace(discipline_name="Math")],
    )
    db = DummyDB(
        session=session,
        strengths=SimpleNamespace(strengths=["Math"], weaknesses=[], partial=False),
        tracks=[track],
    )
    client = _make_test_client(db)

    response = client.get(
        "/api/v1/family/guidance-outcomes",
        headers={"Authorization": "Bearer token"},
        params={"student_session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pending"] is False
    assert len(payload["recommendations"]) == 1
    recommendation = payload["recommendations"][0]
    assert "Professional Track" in recommendation["text"]
    assert recommendation["source"]


def test_guidance_outcomes_returns_pending_when_no_recommendations_generated():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.get(
        "/api/v1/family/guidance-outcomes",
        headers={"Authorization": "Bearer token"},
        params={"student_session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pending"] is True
    assert payload["recommendations"] == []


def test_guidance_outcomes_returns_404_for_unknown_student_session():
    client = _make_test_client(DummyDB(session=None))

    response = client.get(
        "/api/v1/family/guidance-outcomes",
        headers={"Authorization": "Bearer token"},
        params={"student_session_id": str(uuid4())},
    )

    assert response.status_code == 404


def test_guidance_outcomes_returns_404_for_malformed_student_session_id():
    client = _make_test_client(DummyDB(session=None))

    response = client.get(
        "/api/v1/family/guidance-outcomes",
        headers={"Authorization": "Bearer token"},
        params={"student_session_id": "not-a-uuid"},
    )

    assert response.status_code == 404


def test_guidance_outcomes_requires_bearer_authentication():
    client = _make_test_client(DummyDB(session=None))

    response = client.get(
        "/api/v1/family/guidance-outcomes",
        params={"student_session_id": str(uuid4())},
    )

    assert response.status_code in (401, 403)
