from uuid import uuid4

from backend.models.eligibility_simulation_result import EligibilitySimulationResult
from backend.models.secondary_track import SecondaryTrack


def test_eligibility_simulation_result_table_shape():
    table = EligibilitySimulationResult.__table__

    assert table.name == "eligibility_simulation_result"
    assert set(table.columns.keys()) == {
        "id",
        "secondary_track_id",
        "eligible_courses",
        "incomplete_data",
        "message",
    }
    assert table.c.id.primary_key
    assert table.c.secondary_track_id.nullable is False
    assert table.c.eligible_courses.nullable is False
    assert table.c.incomplete_data.nullable is False
    assert table.c.message.nullable is True
    assert table.c.secondary_track_id.foreign_keys
    assert any(
        fk.target_fullname == "secondary_track.id" for fk in table.c.secondary_track_id.foreign_keys
    )


def test_eligibility_simulation_result_has_index_on_secondary_track_id():
    table = EligibilitySimulationResult.__table__

    assert any("secondary_track_id" in index.columns for index in table.indexes)


def test_eligibility_simulation_result_relates_to_secondary_track():
    track_id = uuid4()
    track = SecondaryTrack(id=track_id, name="Science and Technology", description=None)
    result = EligibilitySimulationResult(
        id=uuid4(),
        secondary_track_id=track_id,
        eligible_courses=[{"id": str(uuid4()), "name": "Computer Science"}],
        incomplete_data=False,
        message="Eligibility simulated successfully.",
    )

    track.eligibility_simulation_results.append(result)

    assert result.track is track
    assert result in track.eligibility_simulation_results
    assert result.eligible_courses == [{"id": result.eligible_courses[0]["id"], "name": "Computer Science"}]
    assert result.incomplete_data is False


def test_eligibility_simulation_result_supports_incomplete_data_flag():
    track_id = uuid4()
    result = EligibilitySimulationResult(
        id=uuid4(),
        secondary_track_id=track_id,
        eligible_courses=[],
        incomplete_data=True,
        message="Eligibility cannot be fully assessed due to incomplete or missing data.",
    )

    assert result.incomplete_data is True
    assert result.eligible_courses == []
    assert "incomplete" in result.message.lower()
