from uuid import uuid4

from backend.models.document import Document


def test_document_table_shape():
    table = Document.__table__

    assert table.name == "document"
    assert set(table.columns.keys()) == {
        "id",
        "title",
        "content",
        "source_url",
        "document_type",
        "version_label",
        "indexed",
        "indexing_errors",
        "embedding",
    }
    assert table.c.indexed.type.__class__.__name__ == "Boolean"
    assert table.c.indexing_errors.type.__class__.__name__ == "ARRAY"
    assert table.c.indexing_errors.type.item_type.__class__.__name__ == "Text"
    assert table.c.source_url.unique is True
    assert table.c.source_url.index is not None


def test_document_supports_secondary_track_definitions_document_type():
    document = Document(
        id=uuid4(),
        title="Secondary Track Definitions",
        content="Defines each track's disciplines, exam requirements, and higher education impact.",
        source_url="https://www.dge.mec.pt/definicoes-cursos-secundarios",
        document_type="secondary_track_definitions",
        version_label="2026-edition",
        indexed=True,
        indexing_errors=[],
        embedding=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
    )

    assert document.document_type == "secondary_track_definitions"
    assert document.version_label == "2026-edition"
    assert document.indexed is True
    assert len(document.embedding) == 8


def test_document_stores_multiple_indexing_errors_when_flagged_for_review():
    document = Document(
        id=uuid4(),
        title="Incomplete Secondary Track Definitions",
        content="Defines each track's disciplines only.",
        source_url="https://www.dge.mec.pt/definicoes-incompletas",
        document_type="secondary_track_definitions",
        version_label="2026-edition",
        indexed=False,
        indexing_errors=[
            "Incomplete secondary-track definition: missing exam requirements.",
            "Incomplete secondary-track definition: missing higher education.",
        ],
        embedding=None,
    )

    assert document.indexed is False
    assert len(document.indexing_errors) == 2
    assert document.embedding is None


def test_document_distinguishes_document_types_by_the_document_type_field():
    legal = Document(
        id=uuid4(),
        title="Legal Framework Doc",
        content="content",
        source_url="https://www.dge.mec.pt/legal",
        document_type="legal_framework",
        version_label="v1",
        indexed=True,
        indexing_errors=[],
    )
    secondary_track = Document(
        id=uuid4(),
        title="Secondary Track Doc",
        content="content",
        source_url="https://www.dge.mec.pt/secondary",
        document_type="secondary_track_definitions",
        version_label="v1",
        indexed=True,
        indexing_errors=[],
    )

    assert legal.document_type != secondary_track.document_type
