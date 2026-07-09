from uuid import uuid4

from backend.models.secondary_track import SecondaryTrack, SecondaryTrackDiscipline


def test_secondary_track_discipline_table_shape():
    table = SecondaryTrackDiscipline.__table__

    assert table.name == "secondary_track_discipline"
    assert set(table.columns.keys()) == {"id", "track_id", "discipline_name"}
    assert table.c.id.primary_key
    assert table.c.track_id.nullable is False
    assert table.c.discipline_name.nullable is False
    assert table.c.track_id.foreign_keys
    assert any(fk.target_fullname == "secondary_track.id" for fk in table.c.track_id.foreign_keys)


def test_secondary_track_discipline_relates_to_secondary_track():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    discipline = SecondaryTrackDiscipline(id=uuid4(), track_id=track_id, discipline_name="Mathematics")

    track.disciplines.append(discipline)

    assert discipline.track is track
    assert discipline in track.disciplines
