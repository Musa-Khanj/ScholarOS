from __future__ import annotations

from unittest.mock import MagicMock

from scholaros.ai.llm.message import (
    Message,
    MessageRole,
)
from scholaros.ai.llm.openai import OpenAILLM
from scholaros.ai.llm.response import LLMResponse


def _mock_response() -> MagicMock:

    response = MagicMock()

    response.choices = [
        MagicMock(
            message=MagicMock(
                content="ScholarOS"
            )
        )
    ]

    response.usage = MagicMock(
        prompt_tokens=12,
        completion_tokens=8,
        total_tokens=20,
    )

    return response


def test_model_property() -> None:

    llm = OpenAILLM(
        api_key="test-key",
        model="gpt-test",
    )

    assert llm.model == "gpt-test"


def test_convert_messages() -> None:

    llm = OpenAILLM(
        api_key="test-key",
    )

    messages = [
        Message(
            role=MessageRole.SYSTEM,
            content="system",
        ),
        Message(
            role=MessageRole.USER,
            content="hello",
        ),
    ]

    converted = llm._convert(
        messages,
    )

    assert converted == [
        {
            "role": "system",
            "content": "system",
        },
        {
            "role": "user",
            "content": "hello",
        },
    ]


def test_generate_returns_llm_response() -> None:

    llm = OpenAILLM(
        api_key="test-key",
        model="gpt-test",
    )

    llm._client = MagicMock()

    llm._client.chat.completions.create.return_value = (
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

    assert response.model == "gpt-test"

    assert response.prompt_tokens == 12

    assert response.completion_tokens == 8

    assert response.total_tokens == 20


def test_generate_calls_openai() -> None:

    llm = OpenAILLM(
        api_key="test-key",
    )

    llm._client = MagicMock()

    llm._client.chat.completions.create.return_value = (
        _mock_response()
    )

    messages = [
        Message(
            role=MessageRole.USER,
            content="Hello",
        )
    ]

    llm.generate(
        messages,
    )

    llm._client.chat.completions.create.assert_called_once()


def test_empty_content() -> None:

    response = _mock_response()

    response.choices[0].message.content = None

    llm = OpenAILLM(
        api_key="test-key",
    )

    llm._client = MagicMock()

    llm._client.chat.completions.create.return_value = (
        response
    )

    result = llm.generate(
        [
            Message(
                role=MessageRole.USER,
                content="Hello",
            )
        ]
    )

    assert result.content == ""