from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.higher_ed import get_db_session
from backend.models.higher_ed_course import HigherEdCourse


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, courses=None, fail=False):
        self.courses = courses or []
        self.fail = fail

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
        return DummyResult(self.courses)


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_get_higher_ed_courses_returns_compatible_courses_for_valid_track():
    track_id = uuid4()
    courses = [
        HigherEdCourse(id=uuid4(), name="Computer Science"),
        HigherEdCourse(id=uuid4(), name="Mechanical Engineering"),
    ]
    client = _make_test_client(DummyDB(courses=courses))

    response = client.get(
        "/api/v1/higher-ed/courses", params={"secondary_track_id": str(track_id)}
    )

    assert response.status_code == 200
    assert response.json() == {
        "courses": [
            {"id": str(courses[0].id), "name": "Computer Science"},
            {"id": str(courses[1].id), "name": "Mechanical Engineering"},
        ],
        "message": "",
    }


def test_get_higher_ed_courses_returns_no_data_message_when_no_compatible_courses():
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/higher-ed/courses", params={"secondary_track_id": str(uuid4())}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["courses"] == []
    assert "no data is available" in payload["message"].lower()


def test_get_higher_ed_courses_returns_no_data_message_for_malformed_track_id():
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/higher-ed/courses", params={"secondary_track_id": "not-a-uuid"}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["courses"] == []
    assert "no data is available" in payload["message"].lower()


def test_get_higher_ed_courses_returns_500_on_database_failure():
    client = _make_test_client(DummyDB(fail=True))

    response = client.get(
        "/api/v1/higher-ed/courses", params={"secondary_track_id": str(uuid4())}
    )

    assert response.status_code == 500


def test_get_higher_ed_courses_requires_no_authentication():
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/higher-ed/courses", params={"secondary_track_id": str(uuid4())}
    )

    assert response.status_code == 200
