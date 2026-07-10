from backend.services.chat_service import build_chat_response


def test_requires_confirmation_true_for_critical_decision_terms():
    response = build_chat_response(
        "I want to request an exception for a special case equivalence.", "session-1"
    )

    assert response["requires_confirmation"] is True


def test_requires_confirmation_false_for_a_plain_factual_question_with_a_grounded_answer():
    response = build_chat_response("What are the professional tracks?", "session-2")

    assert response["insufficient_info"] is False
    assert response["requires_confirmation"] is False


def test_requires_confirmation_true_when_no_grounded_answer_is_found():
    response = build_chat_response("What is the weather tomorrow?", "session-3")

    assert response["insufficient_info"] is True
    assert response["requires_confirmation"] is True
    assert "cannot answer" in response["answer"].lower()
