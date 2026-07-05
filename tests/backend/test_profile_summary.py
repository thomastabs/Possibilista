import asyncio
from types import SimpleNamespace
from uuid import uuid4

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
    def __init__(self, interests=None, motivation=None, strengths=None):
        self.interests = interests or []
        self.motivation = motivation
        self.strengths = strengths
        self.executed = []

    async def execute(self, statement):
        self.executed.append(statement)
        entity = statement.column_descriptions[0]["entity"]
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
