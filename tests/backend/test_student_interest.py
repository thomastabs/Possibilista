from backend.models.student_interest import StudentInterest


def test_student_interest_table_shape():
    table = StudentInterest.__table__

    assert table.name == "student_interest"
    assert set(table.columns.keys()) == {"id", "session_id", "interest", "skipped"}
    assert table.c.session_id.foreign_keys
    assert any(fk.target_fullname == "student_session.id" for fk in table.c.session_id.foreign_keys)
    assert any(
        constraint.name and "interest_required_when_not_skipped" in constraint.name
        for constraint in table.constraints
    )

