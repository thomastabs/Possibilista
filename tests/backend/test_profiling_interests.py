import asyncio
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from backend.api.profiling import _parse_interest_payload, record_student_interests


class DummyDB:
    def __init__(self):
        self.records = []
        self.committed = False
        self.rolled_back = False

    def add_all(self, records):
        self.records.extend(records)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def test_parse_interest_payload_valid_interests():
    interests, skipped = _parse_interest_payload({"interests": ["math", "science"], "skipped": False})

    assert interests == ["math", "science"]
    assert skipped is False


def test_parse_interest_payload_valid_skip():
    interests, skipped = _parse_interest_payload({"interests": [], "skipped": True})

    assert interests == []
    assert skipped is True


def test_parse_interest_payload_missing_fields():
    try:
        _parse_interest_payload({"interests": ["math"]})
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("Expected HTTPException for missing fields.")


def test_parse_interest_payload_invalid_types():
    try:
        _parse_interest_payload({"interests": "math", "skipped": "no"})
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("Expected HTTPException for invalid field types.")


def test_record_student_interests_rejects_non_9th_grade():
    db = DummyDB()
    session = SimpleNamespace(id=uuid4(), school_year=10)

    try:
        asyncio.run(record_student_interests(db, session, ["math"], False))
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("Expected HTTPException for non-9th grade session.")


def test_record_student_interests_saves_values_for_ninth_grade():
    db = DummyDB()
    session = SimpleNamespace(id=uuid4(), school_year=9)

    saved = asyncio.run(record_student_interests(db, session, ["math", "science"], False))

    assert saved == 2
    assert db.committed is True
    assert len(db.records) == 2
    assert [record.interest for record in db.records] == ["math", "science"]
    assert all(record.skipped is False for record in db.records)


def test_record_student_interests_saves_skip_for_ninth_grade():
    db = DummyDB()
    session = SimpleNamespace(id=uuid4(), school_year=9)

    saved = asyncio.run(record_student_interests(db, session, [], True))

    assert saved == 1
    assert db.committed is True
    assert len(db.records) == 1
    assert db.records[0].interest is None
    assert db.records[0].skipped is True
