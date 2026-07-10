from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.higher_ed import get_db_session
from backend.models.higher_ed_course import HigherEdCourse
from backend.models.higher_ed_course_entrance_exam import HigherEdCourseEntranceExam


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, course_by_id=None, exams=None, fail=False):
        self.course_by_id = course_by_id or {}
        self.exams = exams or []
        self.fail = fail

    async def get(self, model, record_id):
        if self.fail:
            raise SQLAlchemyError("boom")
        return self.course_by_id.get(record_id)

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
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
