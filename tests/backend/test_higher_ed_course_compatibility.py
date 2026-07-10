from uuid import uuid4

from backend.models.higher_ed_course import HigherEdCourse
from backend.models.higher_ed_course_compatibility import HigherEdCourseCompatibility
from backend.models.secondary_track import SecondaryTrack


def test_higher_ed_course_compatibility_table_shape():
    table = HigherEdCourseCompatibility.__table__

    assert table.name == "higher_ed_course_compatibility"
    assert set(table.columns.keys()) == {
        "id",
        "course_id",
        "secondary_track_id",
        "compatible",
        "message",
    }
    assert table.c.id.primary_key
    assert table.c.course_id.nullable is False
    assert table.c.secondary_track_id.nullable is False
    assert table.c.compatible.nullable is False
    assert table.c.message.nullable is True


def test_higher_ed_course_compatibility_foreign_keys():
    table = HigherEdCourseCompatibility.__table__

    assert table.c.course_id.foreign_keys
    assert any(fk.target_fullname == "higher_ed_course.id" for fk in table.c.course_id.foreign_keys)
    assert table.c.secondary_track_id.foreign_keys
    assert any(
        fk.target_fullname == "secondary_track.id" for fk in table.c.secondary_track_id.foreign_keys
    )


def test_higher_ed_course_compatibility_relates_to_course_and_track():
    course_id = uuid4()
    track_id = uuid4()
    course = HigherEdCourse(id=course_id, name="Computer Science")
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    compatibility = HigherEdCourseCompatibility(
        id=uuid4(),
        course_id=course_id,
        secondary_track_id=track_id,
        compatible=True,
        message="Compatible with this track.",
    )

    course.compatibilities.append(compatibility)
    track.course_compatibilities.append(compatibility)

    assert compatibility.course is course
    assert compatibility.track is track
    assert compatibility in course.compatibilities
    assert compatibility in track.course_compatibilities
    assert compatibility.compatible is True
    assert compatibility.message == "Compatible with this track."
