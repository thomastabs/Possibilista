from uuid import uuid4

from backend.models.student_session import StudentSession


def test_student_session_has_nullable_age_field():
    table = StudentSession.__table__

    assert "age" in table.columns.keys()
    assert table.c.age.nullable is True

    session_with_age = StudentSession(id=uuid4(), age=10)
    session_without_age = StudentSession(id=uuid4(), age=None)

    assert session_with_age.age == 10
    assert session_without_age.age is None


def test_student_session_without_age_remains_valid():
    session = StudentSession(id=uuid4(), school_year=9, student_name="Maria")

    assert session.age is None
    assert session.school_year == 9
    assert session.student_name == "Maria"
