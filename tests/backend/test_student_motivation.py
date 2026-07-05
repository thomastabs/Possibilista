from backend.models.student_motivation import StudentMotivation


def test_student_motivation_table_shape():
    table = StudentMotivation.__table__

    assert table.name == "student_motivation"
    assert set(table.columns.keys()) == {"id", "session_id", "motivations", "declined"}
    assert table.c.motivations.type.__class__.__name__ == "Text"
    assert table.c.declined.type.__class__.__name__ == "Boolean"
    assert table.c.session_id.foreign_keys
    assert any(fk.target_fullname == "student_session.id" for fk in table.c.session_id.foreign_keys)
    assert table.c.session_id.index is not None

