import asyncio
from types import SimpleNamespace
from uuid import uuid4

from backend.models.chat_message import ChatMessage
from backend.services.chat_service import (
    build_chat_response_for_message,
    build_chat_response_with_context,
    get_last_chat_message,
    segment_intents,
)


def test_chat_message_table_shape():
    table = ChatMessage.__table__

    assert table.name == "chat_message"
    assert set(table.columns.keys()) == {
        "id",
        "session_id",
        "message",
        "answer",
        "facts",
        "interpretations",
        "insufficient_info",
        "requires_confirmation",
        "is_fact",
        "is_interpretation",
        "no_basis",
        "previous_message_id",
        "context_tokens",
        "timestamp",
    }
    assert table.c.facts.type.__class__.__name__ == "ARRAY"
    assert table.c.interpretations.type.__class__.__name__ == "ARRAY"
    assert table.c.facts.type.item_type.__class__.__name__ == "Text"
    assert table.c.interpretations.type.item_type.__class__.__name__ == "Text"
    assert table.c.insufficient_info.type.__class__.__name__ == "Boolean"
    assert table.c.requires_confirmation.type.__class__.__name__ == "Boolean"
    assert table.c.session_id.foreign_keys
    assert any(fk.target_fullname == "student_session.id" for fk in table.c.session_id.foreign_keys)
    assert table.c.session_id.index is not None


def test_chat_message_table_has_dialogue_context_fields():
    table = ChatMessage.__table__

    assert table.c.previous_message_id.nullable is True
    assert table.c.context_tokens.nullable is True
    assert table.c.context_tokens.type.__class__.__name__ == "ARRAY"
    assert table.c.context_tokens.type.item_type.__class__.__name__ == "Text"
    assert any(
        fk.target_fullname == "chat_message.id" for fk in table.c.previous_message_id.foreign_keys
    )


def test_chat_message_persists_dialogue_context_fields():
    from uuid import uuid4

    previous_id = uuid4()
    message = ChatMessage(
        session_id=uuid4(),
        message="What subjects does it include?",
        answer="Continuing from the previous topic: ...",
        previous_message_id=previous_id,
        context_tokens=["Professional Courses Guidance"],
    )

    assert message.previous_message_id == previous_id
    assert message.context_tokens == ["Professional Courses Guidance"]


def test_chat_message_defaults_are_empty_and_false():
    from uuid import uuid4

    message = ChatMessage(
        session_id=uuid4(),
        message="What tracks are available?",
        answer="Scientific-humanistic, professional, and specialized artistic tracks.",
    )

    assert message.facts is None or message.facts == []
    assert message.interpretations is None or message.interpretations == []
    assert message.insufficient_info in (None, False)
    assert message.requires_confirmation in (None, False)
    assert message.is_fact in (None, False)
    assert message.is_interpretation in (None, False)
    assert message.no_basis in (None, False)


def test_chat_message_persists_fact_and_interpretation_flags():
    message = ChatMessage(
        session_id=uuid4(),
        message="What are the professional tracks?",
        answer="According to the official documents...",
        is_fact=True,
        is_interpretation=False,
    )

    assert message.is_fact is True
    assert message.is_interpretation is False


def test_chat_message_persists_no_basis_flag():
    message = ChatMessage(
        session_id=uuid4(),
        message="What do you think I should do?",
        answer="I cannot provide an interpretation for this because no source information is available.",
        is_fact=False,
        is_interpretation=False,
        no_basis=True,
    )

    assert message.no_basis is True
    assert message.is_interpretation is False


def test_build_chat_response_with_context_retains_context_for_related_follow_up():
    previous_message = SimpleNamespace(
        id=uuid4(),
        context_tokens=["Professional Courses Guidance"],
        facts=["Professional Courses Guidance (https://www.dge.mec.pt/cursos-profissionais): ..."],
    )

    response = build_chat_response_with_context(
        "What subjects does it include?",
        "session-1",
        previous_message,
    )

    assert response["insufficient_info"] is False
    assert response["facts"] == previous_message.facts
    assert response["previous_message_id"] == str(previous_message.id)
    assert response["context_tokens"] == previous_message.context_tokens
    assert "continuing from the previous topic" in response["answer"].lower()


def test_build_chat_response_with_context_resets_on_abrupt_topic_change():
    previous_message = SimpleNamespace(
        id=uuid4(),
        context_tokens=["Professional Courses Guidance"],
        facts=["Professional Courses Guidance (https://www.dge.mec.pt/cursos-profissionais): ..."],
    )

    response = build_chat_response_with_context(
        "What are the specialized artistic tracks?",
        "session-2",
        previous_message,
    )

    assert response["previous_message_id"] is None
    assert response["context_tokens"] == ["Specialized Artistic Courses Guidance"]
    assert response["facts"] != previous_message.facts


def test_build_chat_response_with_context_has_no_prior_turn():
    response = build_chat_response_with_context(
        "What are the professional tracks?",
        "session-3",
        None,
    )

    assert response["previous_message_id"] is None
    assert response["context_tokens"] == ["Professional Courses Guidance"]


def test_build_chat_response_with_context_handles_previous_message_without_context_tokens():
    previous_message = SimpleNamespace(
        id=uuid4(),
        context_tokens=None,
        facts=["Professional Courses Guidance (https://www.dge.mec.pt/cursos-profissionais): ..."],
    )

    response = build_chat_response_with_context(
        "What subjects does it include?",
        "session-5",
        previous_message,
    )

    assert response["insufficient_info"] is False
    assert response["facts"] == previous_message.facts


def test_build_chat_response_with_context_stays_insufficient_when_previous_turn_has_no_facts():
    previous_message = SimpleNamespace(id=uuid4(), context_tokens=None, facts=[])

    response = build_chat_response_with_context(
        "What is the weather tomorrow?",
        "session-6",
        previous_message,
    )

    assert response["insufficient_info"] is True
    assert response["facts"] == []


def test_segment_intents_leaves_a_straightforward_question_as_one_segment():
    segments = segment_intents("What are the professional tracks?")

    assert segments == ["What are the professional tracks?"]


def test_segment_intents_does_not_split_a_plain_conjunction():
    segments = segment_intents("Which tracks focus on professional and artistic training?")

    assert segments == ["Which tracks focus on professional and artistic training?"]


def test_segment_intents_splits_on_multiple_question_marks():
    segments = segment_intents(
        "What are the professional tracks? What subjects does it include?"
    )

    assert segments == [
        "What are the professional tracks?",
        "What subjects does it include?",
    ]


def test_segment_intents_splits_a_single_sentence_compound_question():
    segments = segment_intents(
        "What are the professional tracks and what subjects do they include?"
    )

    assert segments == [
        "What are the professional tracks",
        "what subjects do they include?",
    ]


def test_segment_intents_splits_compound_question_without_a_trailing_question_mark():
    segments = segment_intents("What are the professional tracks and how do I apply")

    assert segments == [
        "What are the professional tracks",
        "how do I apply",
    ]


def test_segment_intents_degrades_to_one_segment_for_malformed_question_marks():
    segments = segment_intents("What are the professional tracks??")

    assert segments == ["What are the professional tracks?"]


def test_segment_intents_splits_three_part_compound_question():
    segments = segment_intents(
        "What are the professional tracks? "
        "What are the specialized artistic tracks? "
        "What subjects does the professional track include?"
    )

    assert len(segments) == 3


def test_build_chat_response_for_message_straightforward_question_matches_single_intent_path():
    with_context = build_chat_response_for_message(
        "What are the professional tracks?", "session-7", None
    )
    single_intent = build_chat_response_with_context(
        "What are the professional tracks?", "session-7", None
    )

    assert with_context == single_intent


def test_build_chat_response_for_message_segments_a_compound_question():
    response = build_chat_response_for_message(
        "What are the professional tracks? What are the specialized artistic tracks?",
        "session-8",
        None,
    )

    assert response["answer"].startswith("1) ")
    assert "2) " in response["answer"]
    assert any("Professional Courses Guidance" in fact for fact in response["facts"])
    assert any("Specialized Artistic Courses Guidance" in fact for fact in response["facts"])
    assert response["insufficient_info"] is False


def test_build_chat_response_for_message_compound_question_flags_confirmation_from_any_part():
    response = build_chat_response_for_message(
        "What are the professional tracks? Do I need an exception for a special case?",
        "session-9",
        None,
    )

    assert response["requires_confirmation"] is True


def test_build_chat_response_for_message_combines_three_part_compound_question():
    response = build_chat_response_for_message(
        "What are the professional tracks? "
        "What are the specialized artistic tracks? "
        "What is the weather tomorrow?",
        "session-10",
        None,
    )

    assert "1) " in response["answer"]
    assert "2) " in response["answer"]
    assert "3) " in response["answer"]
    assert response["insufficient_info"] is False, (
        "at least one of the three parts (professional/artistic) had a basis, so the "
        "combined response must not report insufficient_info overall"
    )


def test_get_last_chat_message_returns_most_recent_record():
    class DummyResult:
        def __init__(self, record):
            self._record = record

        def scalar_one_or_none(self):
            return self._record

    class DummyDB:
        def __init__(self, record):
            self.record = record
            self.statement = None

        async def execute(self, statement):
            self.statement = statement
            return DummyResult(self.record)

    expected = SimpleNamespace(id=uuid4())
    db = DummyDB(expected)

    result = asyncio.run(get_last_chat_message(db, "session-4"))

    assert result is expected
