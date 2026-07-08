import asyncio
from types import SimpleNamespace
from uuid import uuid4

from backend.models.chat_message import ChatMessage
from backend.services.chat_service import build_chat_response_with_context, get_last_chat_message


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
