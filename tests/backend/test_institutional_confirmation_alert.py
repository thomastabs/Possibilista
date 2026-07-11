from uuid import uuid4

from backend.models.institutional_confirmation_alert import InstitutionalConfirmationAlert
from backend.models.student_session import StudentSession


def test_institutional_confirmation_alert_table_shape():
    table = InstitutionalConfirmationAlert.__table__

    assert table.name == "institutional_confirmation_alert"
    assert set(table.columns.keys()) == {
        "id",
        "session_id",
        "alert_present",
        "alert_message",
    }
    assert table.c.alert_present.type.__class__.__name__ == "Boolean"
    assert table.c.session_id.foreign_keys
    assert any(
        fk.target_fullname == "student_session.id" for fk in table.c.session_id.foreign_keys
    )
    assert table.c.session_id.unique is True
    assert table.c.session_id.index is not None


def test_institutional_confirmation_alert_links_to_a_student_session():
    session_id = uuid4()
    alert = InstitutionalConfirmationAlert(
        id=uuid4(),
        session_id=session_id,
        alert_present=True,
        alert_message="Certain academic choices require confirmation from official institutions.",
    )

    assert alert.session_id == session_id
    assert alert.alert_present is True
    assert (
        alert.alert_message
        == "Certain academic choices require confirmation from official institutions."
    )


def test_institutional_confirmation_alert_defaults_to_no_alert():
    alert = InstitutionalConfirmationAlert(
        id=uuid4(),
        session_id=uuid4(),
        alert_present=False,
        alert_message=None,
    )

    assert alert.alert_present is False
    assert alert.alert_message is None


def test_student_session_exposes_institutional_confirmation_alert_relationship():
    assert "institutional_confirmation_alert" in StudentSession.__mapper__.relationships
