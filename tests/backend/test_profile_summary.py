import asyncio
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from backend.api.profiling import get_profile_summary_endpoint
from backend.services.profile_summary import generate_profile_summary


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def scalar_one_or_none(self):
        return self._records

    def unique(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, session=None, interests=None, motivation=None, strengths=None):
        self.session = session
        self.interests = interests or []
        self.motivation = motivation
        self.strengths = strengths
        self.executed = []

    async def execute(self, statement):
        self.executed.append(statement)
        entity = statement.column_descriptions[0]["entity"]
        if getattr(entity, "__name__", "") == "StudentSession":
            return DummyResult(self.session)
        if getattr(entity, "__name__", "") == "StudentInterest":
            return DummyResult(self.interests)
        if getattr(entity, "__name__", "") == "StudentMotivation":
            return DummyResult(self.motivation)
        if getattr(entity, "__name__", "") == "StudentStrengthWeakness":
            return DummyResult(self.strengths)
        return DummyResult([])


def test_generate_profile_summary_complete_data():
    db = DummyDB(
        interests=[SimpleNamespace(interest="Math", skipped=False)],
        motivation=SimpleNamespace(motivations="I like helping people.", declined=False),
        strengths=SimpleNamespace(
            strengths=["Math", "Science"],
            weaknesses=["History"],
            partial=False,
        ),
    )

    summary = asyncio.run(generate_profile_summary(db, str(uuid4())))

    assert "Interests captured: Math." in summary["profile_summary"]
    assert "Motivations captured: I like helping people." in summary["profile_summary"]
    assert "Academic strengths: Math, Science. Academic weaknesses: History." in summary["profile_summary"]
    assert summary["missing_fields"] == []
    assert summary["suggestions"] == []


def test_generate_profile_summary_missing_and_partial_data():
    db = DummyDB(
        interests=[],
        motivation=SimpleNamespace(motivations="", declined=True),
        strengths=SimpleNamespace(
            strengths=[],
            weaknesses=[],
            partial=True,
        ),
    )

    summary = asyncio.run(generate_profile_summary(db, str(uuid4())))

    assert "No interests have been recorded yet." in summary["profile_summary"]
    assert "Motivation questions were declined." in summary["profile_summary"]
    assert "Academic strengths and weaknesses were provided partially" in summary["profile_summary"]
    assert "interests" in summary["missing_fields"]
    assert "motivations" in summary["missing_fields"]
    assert "academic_strengths_weaknesses" in summary["missing_fields"]
    assert len(summary["suggestions"]) >= 3


def test_profiling_summary_endpoint_returns_complete_payload():
    session = SimpleNamespace(id=uuid4(), school_year=9)
    db = DummyDB(
        session=session,
        interests=[SimpleNamespace(interest="Math", skipped=False)],
        motivation=SimpleNamespace(motivations="I like helping people.", declined=False),
        strengths=SimpleNamespace(
            strengths=["Math", "Science"],
            weaknesses=["History"],
            partial=False,
        ),
    )

    response = asyncio.run(
        get_profile_summary_endpoint(SimpleNamespace(), object(), db=db, student_session=session)
    )

    assert response["status"] == "success"
    assert "profile_summary" in response
    assert "missing_fields" in response
    assert "suggestions" in response
    assert response["missing_fields"] == []


def test_profiling_summary_endpoint_returns_404_when_session_missing():
    session = SimpleNamespace(id=uuid4(), school_year=9)
    db = DummyDB(session=None)

    try:
        asyncio.run(
            get_profile_summary_endpoint(SimpleNamespace(), object(), db=db, student_session=session)
        )
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected HTTPException for missing student session.")
