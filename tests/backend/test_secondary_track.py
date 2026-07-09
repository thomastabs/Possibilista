from backend.models.secondary_track import SecondaryTrack, SecondaryTrackDiscipline


def test_secondary_track_model_and_migration():
    table = SecondaryTrack.__table__

    assert table.name == "secondary_track"
    assert set(table.columns.keys()) == {"id", "name", "description"}
    assert table.c.id.primary_key
    assert table.c.name.nullable is False
    assert table.c.name.unique
    assert table.c.description.nullable is True


def test_secondary_track_discipline_table_shape():
    table = SecondaryTrackDiscipline.__table__

    assert table.name == "secondary_track_discipline"
    assert set(table.columns.keys()) == {"id", "track_id", "discipline_name"}
    assert table.c.track_id.foreign_keys
    assert any(fk.target_fullname == "secondary_track.id" for fk in table.c.track_id.foreign_keys)
