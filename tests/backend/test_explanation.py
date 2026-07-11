from uuid import uuid4

from backend.models.explanation import Explanation


def test_explanation_table_shape():
    table = Explanation.__table__

    assert table.name == "explanation"
    assert set(table.columns.keys()) == {
        "id",
        "explanation_id",
        "facts",
        "interpretations",
        "unavailable_info",
    }
    assert table.c.facts.type.__class__.__name__ == "ARRAY"
    assert table.c.interpretations.type.__class__.__name__ == "ARRAY"
    assert table.c.facts.type.item_type.__class__.__name__ == "Text"
    assert table.c.interpretations.type.item_type.__class__.__name__ == "Text"
    assert table.c.unavailable_info.type.__class__.__name__ == "Boolean"
    assert table.c.explanation_id.unique is True
    assert table.c.explanation_id.index is not None


def test_explanation_stores_facts_interpretations_and_unavailable_info():
    explanation_id = uuid4()
    explanation = Explanation(
        id=uuid4(),
        explanation_id=explanation_id,
        facts=["The professional track leads to a secondary qualification."],
        interpretations=["This may suit a student who prefers hands-on learning."],
        unavailable_info=False,
    )

    assert explanation.explanation_id == explanation_id
    assert explanation.facts == ["The professional track leads to a secondary qualification."]
    assert explanation.interpretations == [
        "This may suit a student who prefers hands-on learning."
    ]
    assert explanation.unavailable_info is False


def test_explanation_defaults_indicate_unavailable_info_flag_is_explicit():
    explanation = Explanation(
        id=uuid4(),
        explanation_id=uuid4(),
        facts=[],
        interpretations=[],
        unavailable_info=True,
    )

    assert explanation.facts == []
    assert explanation.interpretations == []
    assert explanation.unavailable_info is True
