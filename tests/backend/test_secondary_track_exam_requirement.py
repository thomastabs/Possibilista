from uuid import uuid4

from backend.models.secondary_track import SecondaryTrack, SecondaryTrackExamRequirement


def test_secondary_track_exam_requirement_table_shape():
    table = SecondaryTrackExamRequirement.__table__

    assert table.name == "secondary_track_exam_requirement"
    assert set(table.columns.keys()) == {"id", "track_id", "exam_name", "timing"}
    assert table.c.id.primary_key
    assert table.c.track_id.nullable is False
    assert table.c.exam_name.nullable is False
    assert table.c.timing.nullable is False
    assert table.c.track_id.foreign_keys
    assert any(fk.target_fullname == "secondary_track.id" for fk in table.c.track_id.foreign_keys)


def test_secondary_track_exam_requirement_has_index_on_track_id():
    table = SecondaryTrackExamRequirement.__table__

    assert any("track_id" in index.columns for index in table.indexes)


def test_secondary_track_exam_requirement_relates_to_secondary_track():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    exam_requirement = SecondaryTrackExamRequirement(
        id=uuid4(),
        track_id=track_id,
        exam_name="Mathematics A",
        timing="End of 12th grade",
    )

    track.exam_requirements.append(exam_requirement)

    assert exam_requirement.track is track
    assert exam_requirement in track.exam_requirements
