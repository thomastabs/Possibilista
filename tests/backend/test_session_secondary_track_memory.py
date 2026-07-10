from uuid import uuid4

from backend.models.secondary_track import SecondaryTrack
from backend.models.session_secondary_track_memory import SessionSecondaryTrackMemory
from backend.models.student_session import StudentSession


def test_session_secondary_track_memory_table_shape():
    table = SessionSecondaryTrackMemory.__table__

    assert table.name == "session_secondary_track_memory"
    assert set(table.columns.keys()) == {"id", "session_id", "stored_track_id"}
    assert table.c.id.primary_key
    assert table.c.session_id.nullable is False
    assert table.c.stored_track_id.nullable is False
    assert table.c.session_id.foreign_keys
    assert any(
        fk.target_fullname == "student_session.id" for fk in table.c.session_id.foreign_keys
    )
    assert table.c.stored_track_id.foreign_keys
    assert any(
        fk.target_fullname == "secondary_track.id" for fk in table.c.stored_track_id.foreign_keys
    )


def test_session_secondary_track_memory_has_index_on_session_id():
    table = SessionSecondaryTrackMemory.__table__

    assert any("session_id" in index.columns for index in table.indexes)


def test_session_secondary_track_memory_relates_to_student_session():
    session_id = uuid4()
    track_id = uuid4()
    session = StudentSession(id=session_id)
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    memory = SessionSecondaryTrackMemory(
        id=uuid4(), session_id=session_id, stored_track_id=track_id
    )

    session.secondary_track_memory = memory

    assert memory.session is session
    assert session.secondary_track_memory is memory
    assert memory.stored_track_id == track_id
    assert track.id == track_id
