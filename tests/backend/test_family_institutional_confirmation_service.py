import asyncio
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

from backend.services.family_service import get_institutional_confirmation_notification


class DummyResult:
    def __init__(self, record):
        self._record = record

    def scalar_one_or_none(self):
        return self._record


class DummyDB:
    def __init__(self, alert=None):
        self.alert = alert

    async def execute(self, statement):
        return DummyResult(self.alert)


class FailingDB:
    async def execute(self, statement):
        raise SQLAlchemyError("boom")


def test_get_institutional_confirmation_notification_returns_alert_when_present():
    alert = SimpleNamespace(
        alert_present=True,
        alert_message="Certain academic choices require confirmation from official institutions.",
    )
    db = DummyDB(alert=alert)

    result = asyncio.run(get_institutional_confirmation_notification(db, str(uuid4())))

    assert result["alert_present"] is True
    assert result["alert_message"] == alert.alert_message


def test_get_institutional_confirmation_notification_returns_no_alert_when_absent():
    db = DummyDB(alert=None)

    result = asyncio.run(get_institutional_confirmation_notification(db, str(uuid4())))

    assert result["alert_present"] is False
    assert result["alert_message"] == ""


def test_get_institutional_confirmation_notification_returns_no_alert_on_database_error():
    db = FailingDB()

    result = asyncio.run(get_institutional_confirmation_notification(db, str(uuid4())))

    assert result["alert_present"] is False
    assert result["alert_message"] == ""
