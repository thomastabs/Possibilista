from uuid import uuid4

from backend.models.secondary_track import SecondaryTrack, SecondaryTrackDisciplineCombination


def test_secondary_track_discipline_combination_table_shape():
    table = SecondaryTrackDisciplineCombination.__table__

    assert table.name == "secondary_track_discipline_combination"
    assert set(table.columns.keys()) == {
        "id",
        "track_id",
        "trienais",
        "bienais",
        "anuais",
        "combinations",
        "message",
    }
    assert table.c.id.primary_key
    assert table.c.track_id.nullable is False
    assert table.c.track_id.unique
    assert table.c.trienais.nullable is False
    assert table.c.bienais.nullable is False
    assert table.c.anuais.nullable is False
    assert table.c.combinations.nullable is False
    assert table.c.message.nullable is True
    assert table.c.track_id.foreign_keys
    assert any(fk.target_fullname == "secondary_track.id" for fk in table.c.track_id.foreign_keys)


def test_secondary_track_discipline_combination_relates_to_secondary_track():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    combination = SecondaryTrackDisciplineCombination(
        id=uuid4(),
        track_id=track_id,
        trienais=["Mathematics A", "Physics and Chemistry"],
        bienais=["Biology"],
        anuais=["Philosophy"],
        combinations=["Mathematics A + Physics and Chemistry"],
        message=None,
    )

    track.discipline_combination = combination

    assert combination.track is track
    assert track.discipline_combination is combination


def test_secondary_track_discipline_combination_persists_all_discipline_lists_and_message():
    track_id = uuid4()
    combination = SecondaryTrackDisciplineCombination(
        id=uuid4(),
        track_id=track_id,
        trienais=["Mathematics A"],
        bienais=["Biology", "Geology"],
        anuais=["Philosophy"],
        combinations=["Mathematics A + Biology and Geology"],
        message="Some disciplines require prerequisite exams.",
    )

    assert combination.trienais == ["Mathematics A"]
    assert combination.bienais == ["Biology", "Geology"]
    assert combination.anuais == ["Philosophy"]
    assert combination.combinations == ["Mathematics A + Biology and Geology"]
    assert combination.message == "Some disciplines require prerequisite exams."
