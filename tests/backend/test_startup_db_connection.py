import asyncio
import logging

import pytest
from sqlalchemy.exc import OperationalError

import backend.main as main


class _FakeConnectionContextManager:
    def __init__(self, exc=None):
        self._exc = exc

    async def __aenter__(self):
        if self._exc is not None:
            raise self._exc
        return self

    async def __aexit__(self, *args):
        return False


class _FakeEngine:
    def __init__(self, exc=None):
        self._exc = exc

    def connect(self):
        return _FakeConnectionContextManager(self._exc)


def test_startup_event_logs_success_when_connection_succeeds(monkeypatch, caplog):
    monkeypatch.setattr(main, "engine", _FakeEngine())

    with caplog.at_level(logging.INFO):
        asyncio.run(main.startup_event())

    assert any(
        "Successfully connected to the PostgreSQL database" in record.message
        for record in caplog.records
    )


def test_startup_event_logs_authentication_failure_and_reraises(monkeypatch, caplog):
    auth_error = OperationalError(
        "SELECT 1", {}, Exception('password authentication failed for user "possibilista"')
    )
    monkeypatch.setattr(main, "engine", _FakeEngine(exc=auth_error))

    with caplog.at_level(logging.ERROR):
        with pytest.raises(OperationalError):
            asyncio.run(main.startup_event())

    assert any(
        "Failed to authenticate with the PostgreSQL database" in record.message
        for record in caplog.records
    )


def test_startup_event_logs_generic_connection_failure_and_reraises(monkeypatch, caplog):
    connection_error = OperationalError(
        "SELECT 1", {}, Exception("could not connect to server: Connection refused")
    )
    monkeypatch.setattr(main, "engine", _FakeEngine(exc=connection_error))

    with caplog.at_level(logging.ERROR):
        with pytest.raises(OperationalError):
            asyncio.run(main.startup_event())

    assert any(
        "Failed to connect to the PostgreSQL database" in record.message
        for record in caplog.records
    )
    assert not any(
        "authenticate" in record.message.lower() for record in caplog.records
    )


def test_startup_event_logs_unexpected_error_and_reraises(monkeypatch, caplog):
    monkeypatch.setattr(main, "engine", _FakeEngine(exc=RuntimeError("boom")))

    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            asyncio.run(main.startup_event())

    assert any(
        "Unexpected error while verifying PostgreSQL connectivity" in record.message
        for record in caplog.records
    )
