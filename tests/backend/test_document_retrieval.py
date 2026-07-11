import asyncio
from types import SimpleNamespace

from sqlalchemy.exc import SQLAlchemyError

from backend.services.document_retrieval_service import retrieve_relevant_documents


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


def _document(title, content, source_url):
    return SimpleNamespace(title=title, content=content, source_url=source_url)


def test_retrieve_relevant_documents_returns_matching_documents():
    db = DummyDB(
        documents=[
            _document(
                "Professional Courses Guidance",
                "Professional courses combine general education with technical training.",
                "https://www.dge.mec.pt/cursos-profissionais",
            )
        ]
    )

    result = asyncio.run(retrieve_relevant_documents(db, "What are professional courses?"))

    assert result["no_source"] is False
    assert len(result["documents"]) == 1
    assert result["documents"][0]["title"] == "Professional Courses Guidance"
    assert result["documents"][0]["source_url"] == "https://www.dge.mec.pt/cursos-profissionais"


def test_retrieve_relevant_documents_returns_no_source_when_nothing_matches():
    db = DummyDB(documents=[])

    result = asyncio.run(retrieve_relevant_documents(db, "What is the weather tomorrow?"))

    assert result["no_source"] is True
    assert result["documents"] == []


def test_retrieve_relevant_documents_limits_results():
    db = DummyDB(
        documents=[
            _document("Doc 1", "content 1", "https://www.dge.mec.pt/doc-1"),
            _document("Doc 2", "content 2", "https://www.dge.mec.pt/doc-2"),
        ]
    )

    result = asyncio.run(retrieve_relevant_documents(db, "query", limit=2))

    assert len(result["documents"]) == 2


def test_retrieve_relevant_documents_returns_no_source_on_database_error():
    db = FailingDB()

    result = asyncio.run(retrieve_relevant_documents(db, "query"))

    assert result["no_source"] is True
    assert result["documents"] == []
