from backend.models.chat_message import ChatMessage


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
