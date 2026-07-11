import asyncio
import logging

from backend.services.document_ingestion_service import (
    EXAM_GUIDE_MISSING_MESSAGE,
    ingest_exam_guide_document,
)
from backend.services.indexing_status_service import get_indexing_status


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records

    def scalar_one_or_none(self):
        return None


class DummyDB:
    def __init__(self):
        self.added = []
        self.committed = 0

    async def execute(self, statement):
        return DummyResult(self.added)

    def add(self, record):
        self.added.append(record)

    async def commit(self):
        self.committed += 1

    async def rollback(self):
        pass


def test_missing_exam_guide_is_reflected_in_indexing_status_after_ingestion_attempt():
    db = DummyDB()

    ingestion_result = asyncio.run(ingest_exam_guide_document(db, None))
    status = asyncio.run(get_indexing_status(db))

    assert ingestion_result["indexed"] is False
    assert status["exam_guide_status"] == "missing"
    assert any("exam_guide" in error for error in status["errors"])


def test_missing_exam_guide_alerts_administrator_via_error_log(caplog):
    db = DummyDB()

    with caplog.at_level(logging.ERROR):
        asyncio.run(ingest_exam_guide_document(db, None))

    alert_records = [
        record
        for record in caplog.records
        if record.levelno >= logging.ERROR and "General Exam Guide document is missing" in record.message
    ]
    assert len(alert_records) == 1


def test_missing_exam_guide_does_not_proceed_with_indexing():
    db = DummyDB()

    result = asyncio.run(ingest_exam_guide_document(db, None))

    assert result["errors"] == [EXAM_GUIDE_MISSING_MESSAGE]
    assert db.added == []
    assert db.committed == 0


def test_indexing_status_endpoint_error_message_names_exam_guide_specifically():
    db = DummyDB()

    status = asyncio.run(get_indexing_status(db))

    exam_guide_errors = [error for error in status["errors"] if error.startswith("exam_guide")]
    assert exam_guide_errors == ["exam_guide: document is missing."]
