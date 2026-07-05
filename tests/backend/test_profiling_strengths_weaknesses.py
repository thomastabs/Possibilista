import asyncio
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from backend.api.profiling import (
    _parse_strengths_weaknesses_payload,
    recommend_compatible_secondary_tracks,
    submit_student_strengths_weaknesses,
    upsert_student_strength_weakness,
)


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalar_one_or_none(self):
        return self._records

    def scalars(self):
        return self

    def unique(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, existing_profile=None, tracks=None):
        self.existing_profile = existing_profile
        self.tracks = tracks or []
        self.records = []
        self.committed = False
        self.rolled_back = False
        self.executed = []

    async def execute(self, statement):
        self.executed.append(statement)
        entity = statement.column_descriptions[0]["entity"]
        if getattr(entity, "__name__", "") == "StudentStrengthWeakness":
            return DummyResult(self.existing_profile)
        return DummyResult(self.tracks)

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


def make_track(name, disciplines, description=""):
    return SimpleNamespace(
        id=uuid4(),
        name=name,
        description=description,
        disciplines=[SimpleNamespace(discipline_name=value) for value in disciplines],
    )


def test_parse_strengths_weaknesses_payload_valid_full():
    strengths, weaknesses, partial = _parse_strengths_weaknesses_payload(
        {
            "strengths": ["Math", "Science"],
            "weaknesses": ["History"],
            "partial": False,
        }
    )

    assert strengths == ["Math", "Science"]
    assert weaknesses == ["History"]
    assert partial is False


def test_parse_strengths_weaknesses_payload_valid_partial():
    strengths, weaknesses, partial = _parse_strengths_weaknesses_payload(
        {
            "strengths": [],
            "weaknesses": [],
            "partial": True,
        }
    )

    assert strengths == []
    assert weaknesses == []
    assert partial is True


def test_parse_strengths_weaknesses_payload_missing_fields():
    try:
        _parse_strengths_weaknesses_payload({"strengths": ["Math"], "partial": False})
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("Expected HTTPException for missing fields.")


def test_recommend_compatible_secondary_tracks_returns_ids_for_matches():
    db = DummyDB(
        tracks=[
            make_track("Science Track", ["Math", "Science"]),
            make_track("Arts Track", ["Art"]),
        ]
    )

    recommendations = asyncio.run(
        recommend_compatible_secondary_tracks(db, ["Math", "Science"], ["History"], False)
    )

    assert len(recommendations) == 1
    assert recommendations[0] == str(db.tracks[0].id)


def test_recommend_compatible_secondary_tracks_requests_clarification_for_sparse_partial_input():
    db = DummyDB(tracks=[make_track("Science Track", ["Math", "Science"])])

    recommendations = asyncio.run(
        recommend_compatible_secondary_tracks(db, [], [], True)
    )

    assert len(recommendations) == 1
    assert recommendations[0].startswith("Clarification needed:")


def test_upsert_student_strength_weakness_creates_record():
    db = DummyDB()
    session = SimpleNamespace(id=uuid4(), school_year=9)

    record = asyncio.run(
        upsert_student_strength_weakness(db, session, ["Math"], ["History"], False)
    )

    assert db.committed is True
    assert len(db.records) == 1
    assert record.strengths == ["Math"]
    assert record.weaknesses == ["History"]
    assert record.partial is False
    assert record.session_id == session.id


def test_upsert_student_strength_weakness_updates_record():
    existing = SimpleNamespace(strengths=["Math"], weaknesses=["History"], partial=False)
    db = DummyDB(existing_profile=existing)
    session = SimpleNamespace(id=uuid4(), school_year=9)

    record = asyncio.run(
        upsert_student_strength_weakness(db, session, ["Science"], ["Geography"], True)
    )

    assert db.committed is True
    assert len(db.records) == 0
    assert record is existing
    assert existing.strengths == ["Science"]
    assert existing.weaknesses == ["Geography"]
    assert existing.partial is True


def test_submit_student_strengths_weaknesses_partial_response():
    db = DummyDB(tracks=[make_track("Science Track", ["Math", "Science"])])
    session = SimpleNamespace(id=uuid4(), school_year=9)
    request = DummyRequest({"strengths": [], "weaknesses": [], "partial": True})

    response = asyncio.run(
        submit_student_strengths_weaknesses(request, object(), db=db, student_session=session)
    )

    assert response["status"] == "success"
    assert "clarification" in response["message"].lower()
    assert db.committed is True


def test_submit_student_strengths_weaknesses_full_response():
    db = DummyDB(tracks=[make_track("Science Track", ["Math", "Science"])])
    session = SimpleNamespace(id=uuid4(), school_year=9)
    request = DummyRequest({"strengths": ["Math"], "weaknesses": ["History"], "partial": False})

    response = asyncio.run(
        submit_student_strengths_weaknesses(request, object(), db=db, student_session=session)
    )

    assert response["status"] == "success"
    assert "recommended tracks" in response["message"].lower()
    assert str(db.tracks[0].id) in response["message"]
    assert db.committed is True
    assert len(db.records) == 1


def test_upsert_student_strength_weakness_rejects_non_ninth_grade():
    db = DummyDB()
    session = SimpleNamespace(id=uuid4(), school_year=10)

    try:
        asyncio.run(upsert_student_strength_weakness(db, session, ["Math"], ["History"], False))
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("Expected HTTPException for non-9th grade session.")
