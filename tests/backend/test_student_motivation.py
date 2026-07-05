import asyncio
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from backend.api.profiling import (
    _parse_motivation_payload,
    get_current_student_session,
    submit_student_motivations,
    upsert_student_motivation,
)
from backend.models.student_motivation import StudentMotivation


def test_student_motivation_table_shape():
    table = StudentMotivation.__table__

    assert table.name == "student_motivation"
    assert set(table.columns.keys()) == {"id", "session_id", "motivations", "declined"}
    assert table.c.motivations.type.__class__.__name__ == "Text"
    assert table.c.declined.type.__class__.__name__ == "Boolean"
    assert table.c.session_id.foreign_keys
    assert any(fk.target_fullname == "student_session.id" for fk in table.c.session_id.foreign_keys)
    assert table.c.session_id.index is not None


class DummyResult:
    def __init__(self, record):
        self._record = record

    def scalar_one_or_none(self):
        return self._record


class DummyDB:
    def __init__(self, existing=None):
        self.existing = existing
        self.records = []
        self.committed = False
        self.rolled_back = False
        self.executed = []

    async def execute(self, statement):
        self.executed.append(statement)
        return DummyResult(self.existing)

    def add(self, record):
        self.records.append(record)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


class DummyRequest:
    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        return self._payload


def test_parse_motivation_payload_valid_text():
    motivations, declined = _parse_motivation_payload(
        {"motivations": "I want to study science.", "declined": False}
    )

    assert motivations == "I want to study science."
    assert declined is False


def test_parse_motivation_payload_valid_decline():
    motivations, declined = _parse_motivation_payload({"motivations": "", "declined": True})

    assert motivations is None
    assert declined is True


def test_parse_motivation_payload_missing_fields():
    try:
        _parse_motivation_payload({"motivations": "I like science"})
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("Expected HTTPException for missing fields.")


def test_upsert_student_motivation_creates_record():
    db = DummyDB()
    session = SimpleNamespace(id=uuid4(), school_year=9)

    record = asyncio.run(
        upsert_student_motivation(db, session, "I want to improve.", False)
    )

    assert db.committed is True
    assert len(db.records) == 1
    assert record.motivations == "I want to improve."
    assert record.declined is False
    assert record.session_id == session.id


def test_upsert_student_motivation_updates_record():
    existing = SimpleNamespace(motivations="Old", declined=False)
    db = DummyDB(existing=existing)
    session = SimpleNamespace(id=uuid4(), school_year=9)

    record = asyncio.run(upsert_student_motivation(db, session, None, True))

    assert db.committed is True
    assert len(db.records) == 0
    assert record is existing
    assert existing.motivations is None
    assert existing.declined is True


def test_upsert_student_motivation_rejects_non_ninth_grade():
    db = DummyDB()
    session = SimpleNamespace(id=uuid4(), school_year=10)

    try:
        asyncio.run(upsert_student_motivation(db, session, "Motivation", False))
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("Expected HTTPException for non-9th grade session.")


def test_submit_student_motivations_saves_text():
    db = DummyDB()
    session = SimpleNamespace(id=uuid4(), school_year=9)
    request = DummyRequest({"motivations": "I want to learn.", "declined": False})

    response = asyncio.run(submit_student_motivations(request, object(), db=db, student_session=session))

    assert response["status"] == "success"
    assert "saved successfully" in response["message"].lower()
    assert db.committed is True


def test_submit_student_motivations_records_decline():
    db = DummyDB()
    session = SimpleNamespace(id=uuid4(), school_year=9)
    request = DummyRequest({"motivations": "", "declined": True})

    response = asyncio.run(submit_student_motivations(request, object(), db=db, student_session=session))

    assert response["status"] == "success"
    assert "declined" in response["message"].lower()
    assert db.committed is True


def test_get_current_student_session_requires_authentication():
    request = SimpleNamespace(state=SimpleNamespace())

    try:
        asyncio.run(get_current_student_session(request))
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Expected HTTPException for missing session context.")
