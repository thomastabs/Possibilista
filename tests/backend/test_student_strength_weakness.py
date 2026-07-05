from backend.models.student_strength_weakness import StudentStrengthWeakness


def test_student_strength_weakness_table_shape():
    table = StudentStrengthWeakness.__table__

    assert table.name == "student_strength_weakness"
    assert set(table.columns.keys()) == {"id", "session_id", "strengths", "weaknesses", "partial"}
    assert table.c.strengths.type.__class__.__name__ == "ARRAY"
    assert table.c.weaknesses.type.__class__.__name__ == "ARRAY"
    assert table.c.strengths.type.item_type.__class__.__name__ == "Text"
    assert table.c.weaknesses.type.item_type.__class__.__name__ == "Text"
    assert table.c.partial.type.__class__.__name__ == "Boolean"
    assert table.c.session_id.foreign_keys
    assert any(fk.target_fullname == "student_session.id" for fk in table.c.session_id.foreign_keys)
    assert table.c.session_id.index is not None
