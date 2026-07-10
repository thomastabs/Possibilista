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


def test_post_session_name_updates_session_with_provided_name():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/session/name",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "name": "Maria", "skipped": False},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "Maria" in payload["message"]
    assert session.student_name == "Maria"
    assert db.committed is True


def test_post_session_name_clears_name_when_skipped():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9, student_name="Old Name")
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/session/name",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "skipped": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "without personalization" in payload["message"].lower()
    assert session.student_name is None
    assert db.committed is True


def test_post_session_name_rejects_missing_name_when_not_skipped():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/session/name",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "skipped": False},
    )

    assert response.status_code == 400


def test_post_session_name_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/session/name",
        json={"session_id": str(uuid4()), "name": "Maria", "skipped": False},
    )

    assert response.status_code in (401, 403)


def test_post_session_name_returns_401_for_unknown_session():
    client = _make_test_client(DummyDB(session=None))

    response = client.post(
        "/api/v1/session/name",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(uuid4()), "name": "Maria", "skipped": False},
    )

    assert response.status_code == 401


def test_post_session_name_returns_500_on_database_failure():
    session_id = uuid4()
    session = StudentSession(id=session_id, school_year=9)
    client = _make_test_client(DummyDB(session=session, fail_commit=True))

    response = client.post(
        "/api/v1/session/name",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "name": "Maria", "skipped": False},
    )

    assert response.status_code == 500
