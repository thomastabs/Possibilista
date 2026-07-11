import asyncio
from types import SimpleNamespace
from uuid import uuid4

from backend.services.family_service import get_guidance_outcomes


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
    def __init__(self, strengths=None, tracks=None):
        self.strengths = strengths
        self.tracks = tracks or []

    async def execute(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        name = getattr(entity, "__name__", "")
        if name == "StudentStrengthWeakness":
            return DummyResult(self.strengths)
        if name == "SecondaryTrack":
            return DummyResult(self.tracks)
        return DummyResult([])


def test_get_guidance_outcomes_returns_recommendations_with_text_and_source():
    track = SimpleNamespace(
        name="Professional Track",
        description="Combines general education with technical training.",
        disciplines=[SimpleNamespace(discipline_name="Math")],
    )
    db = DummyDB(
        strengths=SimpleNamespace(strengths=["Math"], weaknesses=[], partial=False),
        tracks=[track],
    )

    result = asyncio.run(get_guidance_outcomes(db, str(uuid4())))

    assert result["pending"] is False
    assert len(result["recommendations"]) == 1
    assert "Professional Track" in result["recommendations"][0]["text"]
    assert result["recommendations"][0]["source"]


def test_get_guidance_outcomes_returns_pending_when_no_strengths_weaknesses_recorded():
    db = DummyDB(strengths=None)

    result = asyncio.run(get_guidance_outcomes(db, str(uuid4())))

    assert result["recommendations"] == []
    assert result["pending"] is True


def test_get_guidance_outcomes_returns_pending_when_no_track_scores_above_zero():
    track = SimpleNamespace(
        name="Artistic Track",
        description=None,
        disciplines=[SimpleNamespace(discipline_name="Art")],
    )
    db = DummyDB(
        strengths=SimpleNamespace(strengths=["Math"], weaknesses=[], partial=False),
        tracks=[track],
    )

    result = asyncio.run(get_guidance_outcomes(db, str(uuid4())))

    assert result["recommendations"] == []
    assert result["pending"] is True
