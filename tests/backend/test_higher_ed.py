from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.higher_ed import get_db_session
from backend.models.higher_ed_course import HigherEdCourse
from backend.models.higher_ed_course_compatibility import HigherEdCourseCompatibility
from backend.models.higher_ed_course_entrance_exam import HigherEdCourseEntranceExam
from backend.models.secondary_track import SecondaryTrack


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(
        self,
        course_by_id=None,
        track_by_id=None,
        exams=None,
        courses=None,
        compatibilities=None,
        fail=False,
    ):
        self.course_by_id = course_by_id or {}
        self.track_by_id = track_by_id or {}
        self.exams = exams or []
        self.courses = courses or []
        self.compatibilities = compatibilities or []
        self.fail = fail

    async def get(self, model, record_id):
        if self.fail:
            raise SQLAlchemyError("boom")
        if getattr(model, "__name__", "") == "SecondaryTrack":
            return self.track_by_id.get(record_id)
        return self.course_by_id.get(record_id)

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
        entity = statement.column_descriptions[0]["entity"]
        entity_name = getattr(entity, "__name__", "")
        if entity_name == "HigherEdCourseCompatibility":
            return DummyResult(self.compatibilities)
        if entity_name == "HigherEdCourse":
            return DummyResult(self.courses)
        return DummyResult(self.exams)


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_entrance_exam_endpoint_returns_available_exams_for_valid_course():
    course_id = uuid4()
    course = HigherEdCourse(id=course_id, name="Computer Science")
    exams = [
        HigherEdCourseEntranceExam(id=uuid4(), course_id=course_id, exam_name="Mathematics A", weight=0.4),
        HigherEdCourseEntranceExam(
            id=uuid4(), course_id=course_id, exam_name="Physics and Chemistry", weight=0.6
        ),
    ]
    client = _make_test_client(DummyDB(course_by_id={course_id: course}, exams=exams))

    response = client.get(f"/api/v1/higher-ed/courses/{course_id}/entrance-exams")

    assert response.status_code == 200
    assert response.json() == {
        "available": True,
        "exams": [
            {"name": "Mathematics A", "weight": 0.4},
            {"name": "Physics and Chemistry", "weight": 0.6},
        ],
        "message": "",
    }


def test_entrance_exam_endpoint_returns_unavailable_for_course_without_exams():
    course_id = uuid4()
    course = HigherEdCourse(id=course_id, name="Computer Science")
    client = _make_test_client(DummyDB(course_by_id={course_id: course}))

    response = client.get(f"/api/v1/higher-ed/courses/{course_id}/entrance-exams")

    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is False
    assert payload["exams"] == []
    assert "unavailable" in payload["message"].lower()


def test_entrance_exam_endpoint_returns_unavailable_for_nonexistent_course():
    client = _make_test_client(DummyDB())

    response = client.get(f"/api/v1/higher-ed/courses/{uuid4()}/entrance-exams")

    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is False
    assert payload["exams"] == []
    assert "unavailable" in payload["message"].lower()


def test_entrance_exam_endpoint_rejects_malformed_course_id():
    client = _make_test_client(DummyDB())

    response = client.get("/api/v1/higher-ed/courses/not-a-uuid/entrance-exams")

    assert response.status_code == 400


def test_entrance_exam_endpoint_returns_500_on_database_failure():
    client = _make_test_client(DummyDB(fail=True))

    response = client.get(f"/api/v1/higher-ed/courses/{uuid4()}/entrance-exams")

    assert response.status_code == 500


def test_simulate_eligibility_endpoint_returns_eligible_courses_for_valid_track():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    course_id = uuid4()
    course = HigherEdCourse(id=course_id, name="Computer Science")
    compatibilities = [
        HigherEdCourseCompatibility(
            id=uuid4(), course_id=course_id, secondary_track_id=track_id, compatible=True, message=""
        ),
    ]
    client = _make_test_client(
        DummyDB(track_by_id={track_id: track}, compatibilities=compatibilities, courses=[course])
    )

    response = client.post(
        "/api/v1/higher-ed/eligibility-simulation",
        headers={"Authorization": "Bearer token"},
        json={"secondary_track_id": str(track_id)},
    )

    assert response.status_code == 200
    assert response.json() == {
        "eligible_courses": [{"id": str(course_id), "name": "Computer Science"}],
        "incomplete_data": False,
        "message": "Eligibility simulation completed successfully.",
    }


def test_simulate_eligibility_endpoint_returns_incomplete_data_for_track_without_compatibility_data():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    client = _make_test_client(DummyDB(track_by_id={track_id: track}))

    response = client.post(
        "/api/v1/higher-ed/eligibility-simulation",
        headers={"Authorization": "Bearer token"},
        json={"secondary_track_id": str(track_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["eligible_courses"] == []
    assert payload["incomplete_data"] is True
    assert "incomplete" in payload["message"].lower()


def test_simulate_eligibility_endpoint_rejects_malformed_track_id():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/higher-ed/eligibility-simulation",
        headers={"Authorization": "Bearer token"},
        json={"secondary_track_id": "not-a-uuid"},
    )

    assert response.status_code == 400


def test_simulate_eligibility_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/higher-ed/eligibility-simulation",
        json={"secondary_track_id": str(uuid4())},
    )

    assert response.status_code in (401, 403)


def test_simulate_eligibility_endpoint_returns_500_on_database_failure():
    client = _make_test_client(DummyDB(fail=True))

    response = client.post(
        "/api/v1/higher-ed/eligibility-simulation",
        headers={"Authorization": "Bearer token"},
        json={"secondary_track_id": str(uuid4())},
    )

    assert response.status_code == 500
