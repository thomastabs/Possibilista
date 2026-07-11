from uuid import uuid4

from backend.models.document import EMBEDDING_DIMENSIONS, Document


def test_document_stores_multiple_records_with_unique_ids():
    first = Document(
        id=uuid4(),
        title="Legal Framework Doc",
        content="content one",
        source_url="https://www.dge.mec.pt/legal-one",
        document_type="legal_framework",
        version_label="v1",
        indexed=True,
        indexing_errors=[],
    )
    second = Document(
        id=uuid4(),
        title="Legal Framework Doc Two",
        content="content two",
        source_url="https://www.dge.mec.pt/legal-two",
        document_type="legal_framework",
        version_label="v1",
        indexed=True,
        indexing_errors=[],
    )

    assert first.id != second.id
    assert first.source_url != second.source_url


def test_document_embedding_matches_embedding_dimensions_constant():
    document = Document(
        id=uuid4(),
        title="Higher Education Course Requirements",
        content="Describes entrance exam requirements and admission averages.",
        source_url="https://www.dge.mec.pt/requisitos-ensino-superior",
        document_type="higher_ed_requirements",
        version_label="2026-edition",
        indexed=True,
        indexing_errors=[],
        embedding=[0.0] * EMBEDDING_DIMENSIONS,
    )

    assert len(document.embedding) == EMBEDDING_DIMENSIONS
