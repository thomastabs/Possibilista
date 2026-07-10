from uuid import uuid4

from backend.models.student_session import StudentSession


def test_student_name_field():
    table = StudentSession.__table__

    assert "student_name" in table.columns.keys()
    assert table.c.student_name.nullable is True

    session_with_name = StudentSession(id=uuid4(), school_year=9, student_name="Maria")
    session_without_name = StudentSession(id=uuid4(), school_year=9, student_name=None)

    assert session_with_name.student_name == "Maria"
    assert session_without_name.student_name is None
