from scholaros.research.session import (
    ResearchSession,
)


def create_session() -> ResearchSession:

    return ResearchSession(
        query="What is ScholarOS?",
    )


def test_query():

    session = create_session()

    assert (
        session.query
        ==
        "What is ScholarOS?"
    )


def test_context_default():

    session = create_session()

    assert (
        session.context
        == []
    )


def test_notes_default():

    session = create_session()

    assert (
        session.notes
        == []
    )


def test_result_default():

    session = create_session()

    assert (
        session.result
        is None
    )


def test_id_generated():

    session = create_session()

    assert isinstance(
        session.id,
        str,
    )

    assert (
        len(
            session.id,
        )
        > 0
    )


def test_unique_ids():

    first = create_session()

    second = create_session()

    assert (
        first.id
        != second.id
    )


def test_context_is_independent():

    first = create_session()

    second = create_session()

    first.context.append(
        "Document",
    )

    assert (
        second.context
        == []
    )


def test_notes_are_independent():

    first = create_session()

    second = create_session()

    first.notes.append(
        "Observation",
    )

    assert (
        second.notes
        == []
    )


def test_repr():

    session = create_session()

    expected = (
        "ResearchSession("
        f"id='{session.id}', "
        "query='What is ScholarOS?'"
        ")"
    )

    assert (
        repr(
            session,
        )
        == expected
    )


def test_session_working_memory():
    session = create_session()
    assert session.memory is not None
    session.memory.set("active_hypothesis", "Transformers scale quadratically")
    assert session.memory.get("active_hypothesis") == "Transformers scale quadratically"


def test_session_notes_and_context():
    session = create_session()
    session.add_context("Domain: Natural Language Processing")
    session.add_note("Look into FlashAttention optimizations")

    assert len(session.context) == 1
    assert "Natural Language Processing" in session.context[0]
    assert len(session.notes) == 1
    assert "FlashAttention" in session.notes[0]
    assert session.memory.get("note_1") == "Look into FlashAttention optimizations"


def test_session_record_interaction():
    from scholaros.ai.response import AIResponse
    from scholaros.research.result import ResearchResult

    session = create_session()
    ai_resp = AIResponse(content="Attention is all you need details self-attention.", model="mock-model")
    result = ResearchResult(response=ai_resp)

    session.record_interaction(query="How does self-attention work?", result=result, notes=["Follow up on multi-head"])

    assert session.query == "How does self-attention work?"
    assert session.result is result
    assert len(session.history) == 1
    assert session.history[0]["query"] == "How does self-attention work?"
    assert "self-attention" in session.history[0]["content"]
    assert len(session.notes) == 1
    assert session.notes[0] == "Follow up on multi-head"


def test_session_get_conversation_context():
    from scholaros.ai.response import AIResponse
    from scholaros.research.result import ResearchResult

    session = create_session()
    session.add_context("Focus on computer vision")
    session.add_note("Compare ViT and ConvNet")

    ai_resp = AIResponse(content="Vision Transformers process image patches as tokens.", model="mock-model")
    result = ResearchResult(response=ai_resp)
    session.record_interaction(query="What is ViT?", result=result)

    ctx = session.get_conversation_context()
    assert "Focus on computer vision" in ctx
    assert "Compare ViT and ConvNet" in ctx
    assert "What is ViT?" in ctx
    assert "Vision Transformers process image patches" in ctx


def test_session_to_knowledge_document():
    from scholaros.ai.response import AIResponse
    from scholaros.research.result import ResearchResult

    session = create_session()
    session.title = "NLP Attention Survey"
    session.add_note("Attention weights provide interpretability")

    ai_resp = AIResponse(content="Self-attention allows tokens to attend to each other.", model="mock-model")
    result = ResearchResult(response=ai_resp)
    session.record_interaction(query="Explain attention", result=result)

    doc = session.to_knowledge_document(collection_name="surveys")
    assert doc.title == "NLP Attention Survey"
    assert doc.id == f"session-{session.id}"
    assert "Self-attention allows tokens" in doc.content
    assert "Attention weights provide interpretability" in doc.content
    assert "session_report" in doc.metadata.tags
    assert doc.metadata.custom["session_id"] == session.id
    assert doc.metadata.custom["turn_count"] == 1


def test_session_to_dict():
    session = create_session()
    session.title = "Test Session"
    session.add_note("Note 1")
    d = session.to_dict()

    assert d["id"] == session.id
    assert d["title"] == "Test Session"
    assert d["notes"] == ["Note 1"]
    assert "history" in d
    assert "created_at" in d