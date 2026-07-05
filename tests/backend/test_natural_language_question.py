import asyncio

from backend.services.natural_language_question import answer_natural_language_question


def test_answer_natural_language_question_clear_question():
    response = asyncio.run(
        answer_natural_language_question(
            "What are the available secondary tracks?",
            "session-1",
        )
    )

    assert response["session_id"] == "session-1"
    assert response["clarification_needed"] is False
    assert response["out_of_scope"] is False
    assert response["clarification_options"] == []
    assert "official secondary education guidance" in response["answer"].lower()
    assert response["suggestion"] == ""


def test_answer_natural_language_question_ambiguous_question():
    response = asyncio.run(
        answer_natural_language_question(
            "Tell me about secondary education.",
            "session-2",
        )
    )

    assert response["session_id"] == "session-2"
    assert response["clarification_needed"] is True
    assert response["out_of_scope"] is False
    assert response["clarification_options"]
    assert "official secondary education guidance" in response["answer"].lower()


def test_answer_natural_language_question_out_of_scope_question():
    response = asyncio.run(
        answer_natural_language_question(
            "What is the weather tomorrow?",
            "session-3",
        )
    )

    assert response["session_id"] == "session-3"
    assert response["clarification_needed"] is False
    assert response["out_of_scope"] is True
    assert response["clarification_options"] == []
    assert "human advisor" in response["suggestion"].lower()


def test_answer_natural_language_question_rejects_empty_question():
    try:
        asyncio.run(answer_natural_language_question("   ", "session-4"))
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for an empty question.")
