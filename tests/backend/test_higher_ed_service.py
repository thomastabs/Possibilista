import asyncio
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

from backend.models.higher_ed_course import HigherEdCourse
from backend.models.secondary_track import SecondaryTrack
from backend.services.higher_ed_service import get_compatible_higher_ed_courses


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, track_by_id=None, courses=None, fail=False):
        self.track_by_id = track_by_id or {}
        self.courses = courses or []
        self.fail = fail

    async def get(self, model, record_id):
        if self.fail:
            raise SQLAlchemyError("boom")
        return self.track_by_id.get(record_id)

    async def execute(self, statement):
        if self.fail:
            raise SQLAlchemyError("boom")
        return DummyResult(self.courses)


def test_get_compatible_higher_ed_courses_returns_courses_for_valid_track():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    courses = [
        HigherEdCourse(id=uuid4(), name="Computer Science"),
        HigherEdCourse(id=uuid4(), name="Mechanical Engineering"),
    ]
    db = DummyDB(track_by_id={track_id: track}, courses=courses)

    result = asyncio.run(get_compatible_higher_ed_courses(db, str(track_id)))

    assert result == {
        "courses": [
            {"id": str(courses[0].id), "name": "Computer Science"},
            {"id": str(courses[1].id), "name": "Mechanical Engineering"},
        ],
        "message": "",
    }


def test_get_compatible_higher_ed_courses_returns_no_data_message_when_no_compatible_courses():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    db = DummyDB(track_by_id={track_id: track})

    result = asyncio.run(get_compatible_higher_ed_courses(db, str(track_id)))

    assert result["courses"] == []
    assert "no data is available" in result["message"].lower()


def test_get_compatible_higher_ed_courses_returns_no_data_message_for_unknown_track():
    db = DummyDB()

    result = asyncio.run(get_compatible_higher_ed_courses(db, str(uuid4())))

    assert result["courses"] == []
    assert "no data is available" in result["message"].lower()


def test_get_compatible_higher_ed_courses_returns_no_data_message_for_malformed_id():
    db = DummyDB()

    result = asyncio.run(get_compatible_higher_ed_courses(db, "not-a-uuid"))

    assert result == {
        "courses": [],
        "message": "No data is available for the entered secondary track.",
    }
