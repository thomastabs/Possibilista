import asyncio
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

from backend.models.secondary_track import SecondaryTrack, SecondaryTrackExamRequirement
from backend.services.secondary_track_service import get_exam_requirements_for_track


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, track_by_id=None, exam_requirements=None, fail=False):
        self.track_by_id = track_by_id or {}
        self.exam_requirements = exam_requirements or []
        self.fail = fail

    async def get(self, model, record_id):
        if self.fail:
            raise SQLAlchemyError("boom")
        return self.track_by_id.get(record_id)

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
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
