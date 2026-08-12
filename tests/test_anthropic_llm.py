from __future__ import annotations

from unittest.mock import MagicMock

from scholaros.ai.llm.anthropic import AnthropicLLM
from scholaros.ai.llm.message import (
    Message,
    MessageRole,
)
from scholaros.ai.llm.response import LLMResponse


def _mock_response() -> MagicMock:

    response = MagicMock()

    response.content = [
        MagicMock(
            text="ScholarOS",
        )
    ]

    response.usage = MagicMock(
        input_tokens=15,
        output_tokens=10,
    )

    return response


def test_model_property() -> None:

    llm = AnthropicLLM(
        api_key="test-key",
        model="claude-test",
    )

    assert llm.model == "claude-test"


def test_generate_returns_llm_response() -> None:

    llm = AnthropicLLM(
        api_key="test-key",
        model="claude-test",
    )

    llm._client = MagicMock()

    llm._client.messages.create.return_value = (
        _mock_response()
    )

    response = llm.generate(
        [
            Message(
                role=MessageRole.USER,
                content="Hello",
            )
        ]
    )

    assert isinstance(
        response,
        LLMResponse,
    )

    assert response.content == "ScholarOS"

    assert response.model == "claude-test"

    assert response.prompt_tokens == 15

    assert response.completion_tokens == 10

    assert response.total_tokens == 25


def test_generate_calls_sdk() -> None:

    llm = AnthropicLLM(
        api_key="test-key",
    )

    llm._client = MagicMock()

    llm._client.messages.create.return_value = (
        _mock_response()
    )

    llm.generate(
        [
            Message(
                role=MessageRole.USER,
                content="Hello",
            )
        ]
    )

    llm._client.messages.create.assert_called_once()


def test_system_message_is_extracted() -> None:

    llm = AnthropicLLM(
        api_key="test-key",
    )

    llm._client = MagicMock()

    llm._client.messages.create.return_value = (
        _mock_response()
    )

    llm.generate(
        [
            Message(
                role=MessageRole.SYSTEM,
                content="You are ScholarOS.",
            ),
            Message(
                role=MessageRole.USER,
                content="Hello",
            ),
        ]
    )

    kwargs = (
        llm._client.messages.create.call_args.kwargs
    )

    assert kwargs["system"] == (
        "You are ScholarOS."
    )

    assert kwargs["messages"] == [
        {
            "role": "user",
            "content": "Hello",
        }
    ]


def test_assistant_message_conversion() -> None:

    llm = AnthropicLLM(
        api_key="test-key",
    )

    llm._client = MagicMock()

    llm._client.messages.create.return_value = (
        _mock_response()
    )

    llm.generate(
        [
            Message(
                role=MessageRole.ASSISTANT,
                content="Previous reply",
            )
        ]
    )

    kwargs = (
        llm._client.messages.create.call_args.kwargs
    )

    assert kwargs["messages"] == [
        {
            "role": "assistant",
            "content": "Previous reply",
        }
    ]


def test_multiple_user_messages() -> None:

    llm = AnthropicLLM(
        api_key="test-key",
    )

    llm._client = MagicMock()

    llm._client.messages.create.return_value = (
        _mock_response()
    )

    llm.generate(
        [
            Message(
                role=MessageRole.USER,
                content="First",
            ),
            Message(
                role=MessageRole.USER,
                content="Second",
            ),
        ]
    )

    kwargs = (
        llm._client.messages.create.call_args.kwargs
    )

    assert kwargs["messages"] == [
        {
            "role": "user",
            "content": "First",
        },
        {
            "role": "user",
            "content": "Second",
        },
    ]


def test_without_system_message() -> None:

    llm = AnthropicLLM(
        api_key="test-key",
    )

    llm._client = MagicMock()

    llm._client.messages.create.return_value = (
        _mock_response()
    )

    llm.generate(
        [
            Message(
                role=MessageRole.USER,
                content="Hello",
            )
        ]
    )

    kwargs = (
        llm._client.messages.create.call_args.kwargs
    )

    assert kwargs["system"] is None