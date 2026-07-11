import asyncio
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

from backend.services.family_service import get_fact_interpretation_distinction


class DummyResult:
    def __init__(self, record):
        self._record = record

    def scalar_one_or_none(self):
        return self._record


class DummyDB:
    def __init__(self, explanation=None):
        self.explanation = explanation

    async def execute(self, statement):
        return DummyResult(self.explanation)


class FailingDB:
    async def execute(self, statement):
        raise SQLAlchemyError("boom")


def test_get_fact_interpretation_distinction_returns_facts_for_valid_explanation_id():
    explanation = SimpleNamespace(
        facts=["The professional track leads to a secondary qualification."],
        interpretations=[],
        unavailable_info=False,
    )
    db = DummyDB(explanation=explanation)

    result = asyncio.run(get_fact_interpretation_distinction(db, str(uuid4())))

    assert result["facts"] == explanation.facts
    assert result["unavailable_info"] is False


def test_get_fact_interpretation_distinction_returns_interpretations_for_valid_explanation_id():
    explanation = SimpleNamespace(
        facts=[],
        interpretations=["This may suit a student who prefers hands-on learning."],
        unavailable_info=False,
    )
    db = DummyDB(explanation=explanation)

    result = asyncio.run(get_fact_interpretation_distinction(db, str(uuid4())))

    assert result["interpretations"] == explanation.interpretations
    assert result["unavailable_info"] is False


def test_get_fact_interpretation_distinction_returns_unavailable_when_no_record_exists():
    db = DummyDB(explanation=None)

    result = asyncio.run(get_fact_interpretation_distinction(db, str(uuid4())))

    assert result["facts"] == []
    assert result["interpretations"] == []
    assert result["unavailable_info"] is True


def test_get_fact_interpretation_distinction_returns_unavailable_on_database_error():
    db = FailingDB()

    result = asyncio.run(get_fact_interpretation_distinction(db, str(uuid4())))

    assert result["facts"] == []
    assert result["interpretations"] == []
    assert result["unavailable_info"] is True
