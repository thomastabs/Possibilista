from uuid import uuid4

from backend.models.secondary_track import (
    SecondaryTrack,
    SecondaryTrackDiscipline,
    SecondaryTrackHigherEdImpact,
)


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


def test_secondary_track_higher_ed_impact_model():
    table = SecondaryTrackHigherEdImpact.__table__

    assert table.name == "secondary_track_higher_ed_impact"
    assert set(table.columns.keys()) == {"id", "track_id", "impact_description", "message"}
    assert table.c.id.primary_key
    assert table.c.track_id.nullable is False
    assert table.c.track_id.foreign_keys
    assert any(fk.target_fullname == "secondary_track.id" for fk in table.c.track_id.foreign_keys)
    assert any(fk.ondelete == "CASCADE" for fk in table.c.track_id.foreign_keys)

    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    impact = SecondaryTrackHigherEdImpact(
        id=uuid4(),
        track_id=track_id,
        impact_description="Opens access to STEM higher education courses.",
        message="",
    )

    track.higher_ed_impact = impact

    assert impact.track is track
    assert track.higher_ed_impact is impact
