from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.session import get_db_session
from backend.models.student_session import StudentSession


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


def test_post_session_age_stores_valid_age_and_returns_valid_true():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/session/age",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "age": 10},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert session.age == 10
    assert db.committed is True


def test_post_session_age_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/session/age",
        json={"session_id": str(uuid4()), "age": 10},
    )

    assert response.status_code in (401, 403)


def test_post_session_age_returns_401_for_unknown_session():
    client = _make_test_client(DummyDB(session=None))

    response = client.post(
        "/api/v1/session/age",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(uuid4()), "age": 10},
    )

    assert response.status_code == 401


def test_post_session_age_returns_500_on_database_failure():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    client = _make_test_client(DummyDB(session=session, fail_commit=True))

    response = client.post(
        "/api/v1/session/age",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "age": 10},
    )

    assert response.status_code == 500


def test_post_session_age_validation_accepts_boundary_values():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    client = _make_test_client(DummyDB(session=session))

    for age in (9, 12):
        response = client.post(
            "/api/v1/session/age",
            headers={"Authorization": "Bearer token"},
            json={"session_id": str(session_id), "age": age},
        )
        assert response.status_code == 200
        assert response.json()["valid"] is True
        assert session.age == age


def test_post_session_age_validation_rejects_value_outside_range_and_does_not_persist():
    session_id = uuid4()
    session = StudentSession(id=session_id, age=None)
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/session/age",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "age": 13},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert "valid age" in payload["message"].lower()
    assert session.age is None
    assert db.committed is False


def test_post_session_age_validation_rejects_value_below_range():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/session/age",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "age": 8},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False
