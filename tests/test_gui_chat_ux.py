"""
Tests for Part 5 — Chat UX.

Verifies end-to-end Chat UX requirements:
- Chat session and multi-turn history tracking through AISession & Conversation
- Clear conversation rendering with user/assistant/system message separation
- Surfacing RAG/AI citations and context sources
- Async/non-blocking execution via send_message_async()
- Error surfacing without silent fallback
- Conversation clear & session reset
- Enter and Shift+Enter keyboard navigation
"""

from __future__ import annotations

import tkinter as tk
from unittest.mock import MagicMock, Mock

import pytest

from scholaros.ai.manager import AIManager
from scholaros.ai.response import AIResponse
from scholaros.gui.application import GUIApplication
from scholaros.gui.views.workspace_views import ChatView
from scholaros.gui.window import GUIWindow


# ---------------------------------------------------------------------------
# Test Fixtures (Headless Tk Safe)
# ---------------------------------------------------------------------------

_root: tk.Tk | None = None


def get_test_root() -> tk.Tk:
    global _root
    if _root is None:
        default_root = getattr(tk, "_default_root", None)
        if default_root is not None:
            _root = default_root
        else:
            _root = tk.Tk()
            _root.withdraw()
    return _root


@pytest.fixture
def test_root():
    return get_test_root()


@pytest.fixture
def mock_window(test_root):
    window = Mock(spec=GUIWindow)
    window.root = test_root
    window.set_status = Mock()
    window.get_status = Mock(return_value="Ready")
    return window


@pytest.fixture
def mock_ai_manager():
    """Create a mock AIManager with a controllable provider and AIResponse."""
    manager = Mock(spec=AIManager)
    provider = Mock()
    response = AIResponse(
        content="Artificial intelligence is the simulation of human intelligence.",
        model="gpt-4o",
        metadata={"citations": ["Russell & Norvig (2020)", "Turing (1950)"]},
    )
    provider.generate = Mock(return_value=response)
    manager.select_provider = Mock(return_value=provider)
    manager.default_provider = "openai"
    return manager, provider


# ---------------------------------------------------------------------------
# 1. Multi-turn Session & History Tracking
# ---------------------------------------------------------------------------


def test_chat_multi_turn_history_preservation(mock_window, mock_ai_manager):
    """Verify GUIApplication maintains multi-turn conversation history across turns."""
    manager, provider = mock_ai_manager
    app = GUIApplication(mock_window, ai_manager=manager)

    # Turn 1
    reply1 = app.chat("What is AI?")
    assert reply1 == "Artificial intelligence is the simulation of human intelligence."
    assert app.conversation is not None
    assert len(app.conversation.messages) == 2
    assert app.conversation.messages[0].content == "What is AI?"
    assert app.conversation.messages[0].role.value == "user"
    assert app.conversation.messages[1].content == reply1
    assert app.conversation.messages[1].role.value == "assistant"

    # Turn 2 with different response
    reply2_obj = AIResponse(
        content="Key branches include machine learning, NLP, and robotics.",
        model="gpt-4o",
    )
    provider.generate = Mock(return_value=reply2_obj)

    reply2 = app.chat("What are its main branches?")
    assert reply2 == "Key branches include machine learning, NLP, and robotics."
    assert len(app.conversation.messages) == 4
    assert app.conversation.messages[2].content == "What are its main branches?"
    assert app.conversation.messages[3].content == reply2

    # Verify second generate call received the full prior history in AIRequest
    last_call_req = provider.generate.call_args[0][0]
    assert len(last_call_req.messages) == 3  # Turn 1 user, Turn 1 assistant, Turn 2 user
    assert last_call_req.messages[0].content == "What is AI?"
    assert last_call_req.messages[1].content == reply1
    assert last_call_req.messages[2].content == "What are its main branches?"


# ---------------------------------------------------------------------------
# 2. Conversation Rendering & Visual Styling Tags
# ---------------------------------------------------------------------------


def test_chat_view_rendering_and_styling_tags(test_root, mock_window, mock_ai_manager):
    """Verify ChatView configures styling tags and correctly formats messages."""
    manager, _ = mock_ai_manager
    app = GUIApplication(mock_window, ai_manager=manager)
    view = ChatView(parent=test_root, application=app)

    # Check tags exist on Text widget
    history_widget = view.chat.history
    tags = history_widget.tag_names()
    assert "sender_you" in tags
    assert "sender_scholaros" in tags
    assert "sender_system" in tags
    assert "citations" in tags

    # Send message through view
    resp = view.send_message("Explain transformers")
    assert resp == "Artificial intelligence is the simulation of human intelligence."

    history_text = history_widget.get("1.0", "end")
    assert "You: Explain transformers" in history_text
    assert (
        "ScholarOS: Artificial intelligence is the simulation of human intelligence."
        in history_text
    )


# ---------------------------------------------------------------------------
# 3. Citations & Retrieved Context Surfacing
# ---------------------------------------------------------------------------


def test_chat_surfaces_ai_metadata_citations(test_root, mock_window, mock_ai_manager):
    """Verify citations from AIResponse metadata are surfaced in Chat history."""
    manager, provider = mock_ai_manager
    provider.generate = Mock(
        return_value=AIResponse(
            content="Attention is all you need.",
            model="gpt-4o",
            metadata={"citations": ["Vaswani et al. (2017)", "arXiv:1706.03762"]},
        )
    )
    app = GUIApplication(mock_window, ai_manager=manager)
    view = ChatView(parent=test_root, application=app)

    view.send_message("What introduced self-attention?")

    assert app.last_citations == ["Vaswani et al. (2017)", "arXiv:1706.03762"]
    history_text = view.chat.history.get("1.0", "end")
    assert "📚 Sources: Vaswani et al. (2017), arXiv:1706.03762" in history_text


def test_chat_surfaces_rag_sources(test_root, mock_window):
    """Verify sources from RAGPipeline are surfaced in Chat history."""
    mock_rag = Mock()
    rag_result = Mock()
    rag_result.content = "Information retrieved from vector index."
    rag_result.sources = ["chapter1.pdf", "notes.md"]
    mock_rag.run = Mock(return_value=rag_result)

    app = GUIApplication(mock_window, rag_pipeline=mock_rag)
    view = ChatView(parent=test_root, application=app)

    view.send_message("Summarize documents")

    assert app.last_citations == ["chapter1.pdf", "notes.md"]
    history_text = view.chat.history.get("1.0", "end")
    assert "📚 Sources: chapter1.pdf, notes.md" in history_text


def test_chat_omits_citations_when_empty(test_root, mock_window, mock_ai_manager):
    """Verify no Sources line is rendered when no citations are present."""
    manager, provider = mock_ai_manager
    provider.generate = Mock(
        return_value=AIResponse(
            content="Plain answer without citations.",
            model="gpt-4o",
            metadata={},
        )
    )
    app = GUIApplication(mock_window, ai_manager=manager)
    view = ChatView(parent=test_root, application=app)

    view.send_message("Say hello")
    history_text = view.chat.history.get("1.0", "end")
    assert "📚 Sources:" not in history_text


# ---------------------------------------------------------------------------
# 4. Async / Non-blocking Interaction
# ---------------------------------------------------------------------------


def test_chat_view_send_message_async(test_root, mock_window, mock_ai_manager):
    """Verify send_message_async executes without blocking and triggers completion callback."""
    manager, provider = mock_ai_manager
    app = GUIApplication(mock_window, ai_manager=manager)
    view = ChatView(parent=test_root, application=app)

    completed_result: list[str] = []

    def on_complete(res: str) -> None:
        completed_result.append(res)
        test_root.quit()

    view.send_message_async("Async query", on_complete=on_complete)

    # Process events via Tk event loop
    test_root.after(3000, test_root.quit)
    test_root.mainloop()

    assert len(completed_result) == 1
    assert completed_result[0] == "Artificial intelligence is the simulation of human intelligence."
    assert view.is_generating is False
    assert str(view.chat.send_button["state"]) == "normal"

    history_text = view.chat.history.get("1.0", "end")
    assert "You: Async query" in history_text
    assert (
        "ScholarOS: Artificial intelligence is the simulation of human intelligence."
        in history_text
    )


# ---------------------------------------------------------------------------
# 5. Clean Error Surfacing (No Silent Fallback)
# ---------------------------------------------------------------------------


def test_chat_error_surfacing_synchronous(test_root, mock_window, mock_ai_manager):
    """Verify provider errors are displayed cleanly in chat without crashing or falling back to mock."""
    manager, provider = mock_ai_manager
    provider.generate = Mock(side_effect=RuntimeError("Rate limit exceeded"))

    app = GUIApplication(mock_window, ai_manager=manager)
    view = ChatView(parent=test_root, application=app)

    result = view.send_message("Trigger rate limit")
    assert result is None

    history_text = view.chat.history.get("1.0", "end")
    assert "You: Trigger rate limit" in history_text
    assert "System: Error: Rate limit exceeded" in history_text

    mock_window.set_status.assert_called_with("Error: Rate limit exceeded", error=True)


def test_chat_error_surfacing_asynchronous(test_root, mock_window, mock_ai_manager):
    """Verify async errors invoke on_error and surface in UI history."""
    manager, provider = mock_ai_manager
    provider.generate = Mock(side_effect=RuntimeError("Network timeout"))

    app = GUIApplication(mock_window, ai_manager=manager)
    view = ChatView(parent=test_root, application=app)

    errors_caught: list[Exception] = []

    def on_error(exc: Exception) -> None:
        errors_caught.append(exc)
        test_root.quit()

    view.send_message_async("Trigger network timeout", on_error=on_error)

    test_root.after(3000, test_root.quit)
    test_root.mainloop()

    assert len(errors_caught) == 1
    assert isinstance(errors_caught[0], RuntimeError)
    assert view.is_generating is False
    assert str(view.chat.send_button["state"]) == "normal"

    history_text = view.chat.history.get("1.0", "end")
    assert "System: Error: Network timeout" in history_text


# ---------------------------------------------------------------------------
# 6. Session Clear & Reset
# ---------------------------------------------------------------------------


def test_chat_view_clear_resets_history_and_session(test_root, mock_window, mock_ai_manager):
    """Verify view.clear() clears the UI history and resets backend AISession."""
    manager, _ = mock_ai_manager
    app = GUIApplication(mock_window, ai_manager=manager)
    view = ChatView(parent=test_root, application=app)

    view.send_message("First message")
    assert len(app.conversation.messages) == 2
    assert view.chat.history.get("1.0", "end").strip() != ""

    view.clear()

    # UI cleared
    assert view.chat.history.get("1.0", "end").strip() == ""
    # Backend conversation reset
    assert len(app.conversation.messages) == 0


# ---------------------------------------------------------------------------
# 7. Keyboard Navigation (<Return> & <Shift-Return>)
# ---------------------------------------------------------------------------


def test_chat_keyboard_bindings(test_root):
    """Verify Enter invokes send action and Shift+Enter allows newline insertion."""
    view = ChatView(parent=test_root)
    chat = view.chat

    mock_event = MagicMock()

    # Enter key
    with pytest.MonkeyPatch.context() as mp:
        invoke_mock = Mock()
        mp.setattr(chat.send_button, "invoke", invoke_mock)
        res = chat._on_enter_pressed(mock_event)
        assert res == "break"
        invoke_mock.assert_called_once()

    # Shift+Enter key
    res_shift = chat._on_shift_enter(mock_event)
    assert res_shift is None
