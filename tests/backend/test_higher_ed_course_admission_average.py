from uuid import uuid4

from backend.models.higher_ed_course import HigherEdCourse
from backend.models.higher_ed_course_admission_average import HigherEdCourseAdmissionAverage


def test_higher_ed_course_admission_average_table_shape():
    table = HigherEdCourseAdmissionAverage.__table__

    assert table.name == "higher_ed_course_admission_average"
    assert set(table.columns.keys()) == {
        "id",
        "course_id",
        "admission_average",
        "exam_weights",
        "message",
    }
    assert table.c.id.primary_key
    assert table.c.course_id.nullable is False
    assert table.c.course_id.unique
    assert table.c.admission_average.nullable is True
    assert table.c.exam_weights.nullable is True
    assert table.c.message.nullable is True
    assert table.c.course_id.foreign_keys
    assert any(fk.target_fullname == "higher_ed_course.id" for fk in table.c.course_id.foreign_keys)


def test_higher_ed_course_admission_average_allows_null_admission_average_and_exam_weights():
    course_id = uuid4()
    admission_average = HigherEdCourseAdmissionAverage(
        id=uuid4(),
        course_id=course_id,
        admission_average=None,
        exam_weights=None,
        message="Admission criteria information is not available for the selected course.",
    )

    assert admission_average.admission_average is None
    assert admission_average.exam_weights is None
    assert "not available" in admission_average.message.lower()


def test_higher_ed_course_admission_average_relates_to_higher_ed_course():
    course_id = uuid4()
    course = HigherEdCourse(id=course_id, name="Computer Science")
    admission_average = HigherEdCourseAdmissionAverage(
        id=uuid4(),
        course_id=course_id,
        admission_average=16.5,
        exam_weights=[{"exam_name": "Mathematics A", "weight": 0.4}],
        message="",
    )

    course.admission_average = admission_average

    assert admission_average.course is course
    assert course.admission_average is admission_average
    assert admission_average.admission_average == 16.5
    assert admission_average.exam_weights == [{"exam_name": "Mathematics A", "weight": 0.4}]
