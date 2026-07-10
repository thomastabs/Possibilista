from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.session import get_db_session
from backend.models.student_session import StudentSession
from backend.services.session_service import validate_school_year


class DummyResult:
    def __init__(self, record):
        self._record = record

    def scalar_one_or_none(self):
        return self._record


class DummyDB:
    def __init__(self, session=None, fail_commit=False):
        self.session = session
        self.fail_commit = fail_commit
        self.committed = False
        self.rolled_back = False

    async def execute(self, statement):
        return DummyResult(self.session)

    async def commit(self):
        if self.fail_commit:
            raise SQLAlchemyError("boom")
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _make_test_client(db: DummyDB) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[get_db_session] = lambda: db
    return TestClient(app)


def test_student_session_has_nullable_school_year_field():
    table = StudentSession.__table__

    assert "school_year" in table.columns.keys()
    assert table.c.school_year.nullable is True

    session_with_year = StudentSession(id=uuid4(), school_year=10)
    session_without_year = StudentSession(id=uuid4(), school_year=None)

    assert session_with_year.school_year == 10
    assert session_without_year.school_year is None


def test_post_school_year_updates_session_for_valid_year():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/session/school-year",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "school_year": 9},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert session.school_year == 9
    assert db.committed is True


def test_post_school_year_accepts_boundary_values():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/session/school-year",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "school_year": 12},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert session.school_year == 12


def test_post_school_year_rejects_value_outside_range_and_does_not_persist():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=None)
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/session/school-year",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "school_year": 13},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert "valid school year" in payload["message"].lower()
    assert session.school_year is None
    assert db.committed is False


def test_post_school_year_rejects_value_below_range():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/session/school-year",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "school_year": 8},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False


def test_post_school_year_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/session/school-year",
        json={"session_id": str(uuid4()), "school_year": 9},
    )

    assert response.status_code in (401, 403)


def test_post_school_year_returns_401_for_unknown_session():
    client = _make_test_client(DummyDB(session=None))

    response = client.post(
        "/api/v1/session/school-year",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(uuid4()), "school_year": 9},
    )

    assert response.status_code == 401


def test_post_school_year_returns_500_on_database_failure():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    client = _make_test_client(DummyDB(session=session, fail_commit=True))

    response = client.post(
        "/api/v1/session/school-year",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "school_year": 9},
    )

    assert response.status_code == 500


def test_validate_school_year_accepts_values_in_range():
    for year in (9, 10, 11, 12):
        is_valid, message = validate_school_year(year)
        assert is_valid is True
        assert message == ""


def test_validate_school_year_rejects_values_outside_range():
    for year in (8, 13, 0, -1):
        is_valid, message = validate_school_year(year)
        assert is_valid is False
        assert "valid school year" in message.lower()
