from backend.services.chat_service import build_chat_response, detect_critical_decision, suggest_escalation


def test_detect_critical_decision_true_for_context_with_critical_terms():
    assert detect_critical_decision("I want to switch track next year.") is True


def test_detect_critical_decision_false_for_context_without_critical_terms():
    assert detect_critical_decision("What are the professional tracks?") is False


def test_detect_critical_decision_is_case_insensitive():
    assert detect_critical_decision("I NEED TO DROP OUT this year.") is True


def test_suggest_escalation_returns_a_human_confirmation_message():
    suggestion = suggest_escalation("I want to switch track next year.")

    assert "human" in suggestion.lower() or "institution" in suggestion.lower()


def test_requires_confirmation_true_for_critical_decision_terms():
    response = build_chat_response(
        "I want to request an exception for a special case equivalence.", "session-1"
    )

    assert response["requires_confirmation"] is True


def test_requires_confirmation_false_for_a_plain_factual_question_with_a_grounded_answer():
    response = build_chat_response("What are the professional tracks?", "session-2")

    assert response["insufficient_info"] is False
    assert response["requires_confirmation"] is False
    assert response["is_fact"] is True
    assert response["is_interpretation"] is False


def test_is_interpretation_true_for_an_advice_question():
    response = build_chat_response("Which professional track would you recommend for me?", "session-4")

    assert response["is_interpretation"] is True


def test_requires_confirmation_true_when_no_grounded_answer_is_found():
    response = build_chat_response("What is the weather tomorrow?", "session-3")

    assert response["insufficient_info"] is True
    assert response["requires_confirmation"] is True
    assert "cannot answer" in response["answer"].lower()
