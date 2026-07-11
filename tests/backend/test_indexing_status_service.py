import asyncio
from types import SimpleNamespace

from sqlalchemy.exc import SQLAlchemyError

from backend.services.indexing_status_service import get_indexing_status


class DummyResult:
    def __init__(self, records):
        self._records = records

    def scalars(self):
        return self

    def all(self):
        return self._records


class DummyDB:
    def __init__(self, documents=None):
        self.documents = documents or []

    async def execute(self, statement):
        return DummyResult(self.documents)


class FailingDB:
    async def execute(self, statement):
        raise SQLAlchemyError("boom")


def _document(document_type, indexed, indexing_errors=None):
    return SimpleNamespace(
        document_type=document_type, indexed=indexed, indexing_errors=indexing_errors or []
    )


def test_get_indexing_status_reports_missing_for_all_types_when_no_documents_exist():
    db = DummyDB(documents=[])

    result = asyncio.run(get_indexing_status(db))

    assert result["legal_framework_status"] == "missing"
    assert result["exam_guide_status"] == "missing"
    assert result["secondary_track_definitions_status"] == "missing"
    assert result["higher_ed_requirements_status"] == "missing"
    assert len(result["errors"]) == 4


def test_get_indexing_status_reports_indexed_when_document_is_indexed_without_errors():
    db = DummyDB(documents=[_document("legal_framework", indexed=True)])

    result = asyncio.run(get_indexing_status(db))

    assert result["legal_framework_status"] == "indexed"
    assert result["exam_guide_status"] == "missing"
    assert not any("legal_framework" in error for error in result["errors"])


def test_get_indexing_status_reports_failed_when_document_exists_but_not_indexed():
    db = DummyDB(
        documents=[
            _document(
                "exam_guide",
                indexed=False,
                indexing_errors=["general-exam-guide-2026: database persistence failed."],
            )
        ]
    )

    result = asyncio.run(get_indexing_status(db))

    assert result["exam_guide_status"] == "failed"
    assert "general-exam-guide-2026: database persistence failed." in result["errors"]


def test_get_indexing_status_aggregates_errors_across_document_types():
    db = DummyDB(
        documents=[
            _document("legal_framework", indexed=True),
            _document("exam_guide", indexed=False, indexing_errors=["exam guide failed."]),
        ]
    )

    result = asyncio.run(get_indexing_status(db))

    assert result["legal_framework_status"] == "indexed"
    assert result["exam_guide_status"] == "failed"
    assert result["secondary_track_definitions_status"] == "missing"
    assert result["higher_ed_requirements_status"] == "missing"
    assert "exam guide failed." in result["errors"]
    assert any("secondary_track_definitions" in error for error in result["errors"])
    assert any("higher_ed_requirements" in error for error in result["errors"])


def test_get_indexing_status_degrades_gracefully_on_database_error():
    db = FailingDB()

    result = asyncio.run(get_indexing_status(db))

    assert result["legal_framework_status"] == "missing"
    assert result["exam_guide_status"] == "missing"
    assert len(result["errors"]) == 4
