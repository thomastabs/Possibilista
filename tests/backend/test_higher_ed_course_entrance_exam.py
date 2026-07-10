from uuid import uuid4

from backend.models.higher_ed_course import HigherEdCourse
from backend.models.higher_ed_course_entrance_exam import HigherEdCourseEntranceExam


def test_higher_ed_course_entrance_exam_table_shape():
    table = HigherEdCourseEntranceExam.__table__

    assert table.name == "higher_ed_course_entrance_exam"
    assert set(table.columns.keys()) == {"id", "course_id", "exam_name", "weight"}
    assert table.c.id.primary_key
    assert table.c.course_id.nullable is False
    assert table.c.exam_name.nullable is False
    assert table.c.weight.nullable is False
    assert table.c.course_id.foreign_keys
    assert any(fk.target_fullname == "higher_ed_course.id" for fk in table.c.course_id.foreign_keys)


def test_higher_ed_course_entrance_exam_has_index_on_course_id():
    table = HigherEdCourseEntranceExam.__table__

    assert any("course_id" in index.columns for index in table.indexes)


def test_higher_ed_course_entrance_exam_relates_to_higher_ed_course():
    course_id = uuid4()
    course = HigherEdCourse(id=course_id, name="Computer Science")
    exam = HigherEdCourseEntranceExam(
        id=uuid4(), course_id=course_id, exam_name="Mathematics A", weight=0.4
    )

    course.entrance_exams.append(exam)

    assert exam.course is course
    assert exam in course.entrance_exams
    assert exam.weight == 0.4
