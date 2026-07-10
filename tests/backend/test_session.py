import asyncio
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.api import router as api_router
from backend.api.session import get_db_session
from backend.models.student_session import StudentSession
from backend.services.session_service import record_student_interests


class DummyResult:
    def __init__(self, record):
        self._record = record

    def scalar_one_or_none(self):
        return self._record

    def scalars(self):
        return self

    def one_or_none(self):
        return self._record


class DummyDB:
    def __init__(self, session=None, fail_commit=False, track_memory=None):
        self.session = session
        self.fail_commit = fail_commit
        self.committed = False
        self.rolled_back = False
        self.added = []
        self.track_memory = track_memory

    async def execute(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        entity_name = getattr(entity, "__name__", "")
        if entity_name == "SessionSecondaryTrackMemory":
            return DummyResult(self.track_memory)
        return DummyResult(self.session)

    def add_all(self, records):
        self.added.extend(records)

    def add(self, record):
        self.added.append(record)

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


def test_post_session_interests_stores_interests_and_returns_success():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/session/interests",
        headers={"Authorization": "Bearer token"},
        json={
            "session_id": str(session_id),
            "interests": ["Robotics", " Music "],
            "skipped": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert len(db.added) == 2
    assert {record.interest for record in db.added} == {"Robotics", "Music"}
    assert all(record.skipped is False for record in db.added)
    assert all(record.session_id == session_id for record in db.added)
    assert db.committed is True


def test_post_session_interests_records_skip_marker_when_skipped():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    db = DummyDB(session=session)
    client = _make_test_client(db)

    response = client.post(
        "/api/v1/session/interests",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "interests": [], "skipped": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert len(db.added) == 1
    assert db.added[0].skipped is True
    assert db.added[0].interest is None
    assert db.committed is True


def test_post_session_interests_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/session/interests",
        json={"session_id": str(uuid4()), "interests": ["Music"], "skipped": False},
    )

    assert response.status_code in (401, 403)


def test_post_session_interests_returns_401_for_unknown_session():
    client = _make_test_client(DummyDB(session=None))

    response = client.post(
        "/api/v1/session/interests",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(uuid4()), "interests": ["Music"], "skipped": False},
    )

    assert response.status_code == 401


def test_post_session_interests_returns_500_on_database_failure():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    client = _make_test_client(DummyDB(session=session, fail_commit=True))

    response = client.post(
        "/api/v1/session/interests",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "interests": ["Music"], "skipped": False},
    )

    assert response.status_code == 500


def test_record_student_interests_saves_normalized_interests():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    db = DummyDB(session=session)

    saved = asyncio.run(record_student_interests(db, session, ["Robotics", " Music ", ""], False))

    assert saved == 2
    assert db.committed is True
    assert [record.interest for record in db.added] == ["Robotics", "Music"]
    assert all(record.skipped is False for record in db.added)
    assert all(record.session_id == session_id for record in db.added)


def test_record_student_interests_saves_skip_marker_when_skipped():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    db = DummyDB(session=session)

    saved = asyncio.run(record_student_interests(db, session, [], True))

    assert saved == 0
    assert db.committed is True
    assert len(db.added) == 1
    assert db.added[0].interest is None
    assert db.added[0].skipped is True


def test_record_student_interests_saves_skip_marker_when_interests_empty_even_if_not_skipped():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    db = DummyDB(session=session)

    saved = asyncio.run(record_student_interests(db, session, ["   "], False))

    assert saved == 0
    assert len(db.added) == 1
    assert db.added[0].skipped is True


def test_record_student_interests_raises_http_500_on_commit_failure():
    from fastapi import HTTPException

    session_id = uuid4()
    session = StudentSession(id=session_id)
    db = DummyDB(session=session, fail_commit=True)

    try:
        asyncio.run(record_student_interests(db, session, ["Music"], False))
    except HTTPException as exc:
        assert exc.status_code == 500
    else:
        raise AssertionError("Expected HTTPException on commit failure.")


def test_secondary_track_memory_endpoint_returns_stored_track_when_explored():
    from backend.models.session_secondary_track_memory import SessionSecondaryTrackMemory

    session_id = uuid4()
    track_id = uuid4()
    session = StudentSession(id=session_id)
    memory = SessionSecondaryTrackMemory(id=uuid4(), session_id=session_id, stored_track_id=track_id)
    client = _make_test_client(DummyDB(session=session, track_memory=memory))

    response = client.get(
        "/api/v1/session/secondary-track-memory",
        headers={"Authorization": "Bearer token"},
        params={"session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["track_explored"] is True
    assert payload["stored_track_id"] == str(track_id)


def test_secondary_track_memory_endpoint_prompts_exploration_when_none_stored():
    session_id = uuid4()
    session = StudentSession(id=session_id)
    client = _make_test_client(DummyDB(session=session))

    response = client.get(
        "/api/v1/session/secondary-track-memory",
        headers={"Authorization": "Bearer token"},
        params={"session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["track_explored"] is False
    assert payload["stored_track_id"] is None
    assert "explore" in payload["message"].lower()


def test_secondary_track_memory_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.get(
        "/api/v1/session/secondary-track-memory",
        params={"session_id": str(uuid4())},
    )

    assert response.status_code in (401, 403)


def test_secondary_track_memory_endpoint_returns_401_for_unknown_session():
    client = _make_test_client(DummyDB(session=None))

    response = client.get(
        "/api/v1/session/secondary-track-memory",
        headers={"Authorization": "Bearer token"},
        params={"session_id": str(uuid4())},
    )

    assert response.status_code == 401


def test_secondary_track_memory_update_endpoint_creates_memory_and_reflects_in_get():
    from backend.services.session_service import update_secondary_track_memory

    session_id = uuid4()
    track_id = uuid4()
    session = StudentSession(id=session_id)
    db = DummyDB(session=session)

    memory = asyncio.run(update_secondary_track_memory(db, str(session_id), str(track_id)))

    assert memory.session_id == session_id
    assert memory.stored_track_id == track_id
    assert db.committed is True
    assert len(db.added) == 1

    # Reflect the created memory in a fresh DummyDB simulating the GET lookup.
    get_db = DummyDB(session=session, track_memory=memory)
    client = _make_test_client(get_db)
    response = client.get(
        "/api/v1/session/secondary-track-memory",
        headers={"Authorization": "Bearer token"},
        params={"session_id": str(session_id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["track_explored"] is True
    assert payload["stored_track_id"] == str(track_id)


def test_secondary_track_memory_update_endpoint_updates_existing_memory():
    from backend.models.session_secondary_track_memory import SessionSecondaryTrackMemory
    from backend.services.session_service import update_secondary_track_memory

    session_id = uuid4()
    old_track_id = uuid4()
    new_track_id = uuid4()
    session = StudentSession(id=session_id)
    existing_memory = SessionSecondaryTrackMemory(
        id=uuid4(), session_id=session_id, stored_track_id=old_track_id
    )
    db = DummyDB(session=session, track_memory=existing_memory)

    memory = asyncio.run(update_secondary_track_memory(db, str(session_id), str(new_track_id)))

    assert memory is existing_memory
    assert memory.stored_track_id == new_track_id
    assert db.committed is True
    assert db.added == []


def test_secondary_track_memory_update_endpoint_returns_401_for_unknown_session():
    from fastapi import HTTPException

    from backend.services.session_service import update_secondary_track_memory

    db = DummyDB(session=None)

    try:
        asyncio.run(update_secondary_track_memory(db, str(uuid4()), str(uuid4())))
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Expected HTTPException for unknown session.")


def test_secondary_track_memory_update_endpoint_rejects_malformed_ids():
    from fastapi import HTTPException

    from backend.services.session_service import update_secondary_track_memory

    db = DummyDB()

    try:
        asyncio.run(update_secondary_track_memory(db, "not-a-uuid", "not-a-uuid"))
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("Expected HTTPException for malformed ids.")


def test_post_secondary_track_memory_endpoint_returns_success():
    session_id = uuid4()
    track_id = uuid4()
    session = StudentSession(id=session_id)
    client = _make_test_client(DummyDB(session=session))

    response = client.post(
        "/api/v1/session/secondary-track-memory",
        headers={"Authorization": "Bearer token"},
        json={"session_id": str(session_id), "track_id": str(track_id)},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_post_secondary_track_memory_endpoint_requires_bearer_authentication():
    client = _make_test_client(DummyDB())

    response = client.post(
        "/api/v1/session/secondary-track-memory",
        json={"session_id": str(uuid4()), "track_id": str(uuid4())},
    )

    assert response.status_code in (401, 403)
