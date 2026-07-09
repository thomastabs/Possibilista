import asyncio
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

from backend.models.secondary_track import (
    SecondaryTrack,
    SecondaryTrackDisciplineCombination,
    SecondaryTrackExamRequirement,
    SecondaryTrackHigherEdImpact,
)
from backend.services.secondary_track_service import (
    get_discipline_combinations_for_track,
    get_exam_requirements_for_track,
    get_higher_ed_impact_for_track,
)


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records

    def one_or_none(self):
        return self._records[0] if self._records else None


class DummyDB:
    def __init__(
        self,
        track_by_id=None,
        exam_requirements=None,
        discipline_combination=None,
        higher_ed_impact=None,
        fail=False,
    ):
        self.track_by_id = track_by_id or {}
        self.exam_requirements = exam_requirements or []
        self.discipline_combination = discipline_combination
        self.higher_ed_impact = higher_ed_impact
        self.fail = fail

    async def get(self, model, record_id):
        if self.fail:
            raise SQLAlchemyError("boom")
        return self.track_by_id.get(record_id)

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
        entity = statement.column_descriptions[0]["entity"]
        entity_name = getattr(entity, "__name__", "")
        if entity_name == "SecondaryTrackDisciplineCombination":
            records = [self.discipline_combination] if self.discipline_combination else []
            return DummyResult(records)
        if entity_name == "SecondaryTrackHigherEdImpact":
            records = [self.higher_ed_impact] if self.higher_ed_impact else []
            return DummyResult(records)
        return DummyResult(self.exam_requirements)


def test_get_exam_requirements_for_track_returns_exams_for_valid_track():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    exam_requirements = [
        SecondaryTrackExamRequirement(
            id=uuid4(), track_id=track_id, exam_name="Mathematics A", timing="End of 12th grade"
        ),
        SecondaryTrackExamRequirement(
            id=uuid4(), track_id=track_id, exam_name="Physics and Chemistry", timing="End of 11th grade"
        ),
    ]
    db = DummyDB(track_by_id={track_id: track}, exam_requirements=exam_requirements)

    result = asyncio.run(get_exam_requirements_for_track(db, str(track_id)))

    assert result == {
        "valid": True,
        "exams": [
            {"exam_name": "Mathematics A", "timing": "End of 12th grade"},
            {"exam_name": "Physics and Chemistry", "timing": "End of 11th grade"},
        ],
        "message": "Exam requirements retrieved successfully.",
    }


def test_get_exam_requirements_for_track_returns_invalid_for_unknown_track():
    db = DummyDB()

    result = asyncio.run(get_exam_requirements_for_track(db, str(uuid4())))

    assert result["valid"] is False
    assert result["exams"] == []
    assert "no information is available" in result["message"].lower()


def test_get_exam_requirements_for_track_returns_invalid_for_malformed_id():
    db = DummyDB()

    result = asyncio.run(get_exam_requirements_for_track(db, "not-a-uuid"))

    assert result == {
        "valid": False,
        "exams": [],
        "message": "Invalid track ID format.",
    }


def test_get_discipline_combinations_for_track_returns_combinations_for_valid_track():
    track_id = uuid4()
    combination = SecondaryTrackDisciplineCombination(
        id=uuid4(),
        track_id=track_id,
        trienais=["Mathematics A"],
        bienais=["Biology"],
        anuais=["Philosophy"],
        combinations=["Mathematics A + Biology"],
        message="",
    )
    db = DummyDB(discipline_combination=combination)

    result = asyncio.run(get_discipline_combinations_for_track(db, str(track_id)))

    assert result == {
        "valid": True,
        "trienais": ["Mathematics A"],
        "bienais": ["Biology"],
        "anuais": ["Philosophy"],
        "combinations": ["Mathematics A + Biology"],
        "message": "",
    }


def test_get_discipline_combinations_for_track_returns_invalid_when_no_combinations_exist():
    db = DummyDB()

    result = asyncio.run(get_discipline_combinations_for_track(db, str(uuid4())))

    assert result["valid"] is False
    assert result["trienais"] == []
    assert result["bienais"] == []
    assert result["anuais"] == []
    assert result["combinations"] == []
    assert "no valid discipline combinations" in result["message"].lower()


def test_get_discipline_combinations_for_track_returns_invalid_for_malformed_id():
    db = DummyDB()

    result = asyncio.run(get_discipline_combinations_for_track(db, "not-a-uuid"))

    assert result == {
        "valid": False,
        "trienais": [],
        "bienais": [],
        "anuais": [],
        "combinations": [],
        "message": "Invalid track ID format.",
    }


def test_get_higher_ed_impact_for_track_returns_impact_for_valid_track():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    impact = SecondaryTrackHigherEdImpact(
        id=uuid4(),
        track_id=track_id,
        impact_description="Opens access to STEM higher education courses.",
        message="Higher education impact retrieved successfully.",
    )
    db = DummyDB(track_by_id={track_id: track}, higher_ed_impact=impact)

    result = asyncio.run(get_higher_ed_impact_for_track(db, str(track_id)))

    assert result == {
        "valid": True,
        "impact_description": "Opens access to STEM higher education courses.",
        "message": "Higher education impact retrieved successfully.",
    }


def test_get_higher_ed_impact_for_track_returns_valid_true_with_no_data_for_track_without_impact():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    db = DummyDB(track_by_id={track_id: track})

    result = asyncio.run(get_higher_ed_impact_for_track(db, str(track_id)))

    assert result["valid"] is True
    assert result["impact_description"] == ""
    assert "no higher education impact information" in result["message"].lower()


def test_get_higher_ed_impact_for_track_returns_invalid_for_malformed_id():
    db = DummyDB()

    result = asyncio.run(get_higher_ed_impact_for_track(db, "not-a-uuid"))

    assert result == {
        "valid": False,
        "impact_description": "",
        "message": "Invalid track ID format.",
    }


def test_get_higher_ed_impact_for_track_returns_invalid_for_nonexistent_track():
    db = DummyDB()

    result = asyncio.run(get_higher_ed_impact_for_track(db, str(uuid4())))

    assert result["valid"] is False
    assert result["impact_description"] == ""
    assert "not recognized" in result["message"].lower()
