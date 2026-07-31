from __future__ import annotations

from scholaros.ai.ollama_client import OllamaClient
from scholaros.ai.response import AIResponse
from unittest.mock import MagicMock


def test_build_payload():

    client = OllamaClient()

    payload = client._build_payload(
        model="qwen2.5:1.5b",
        prompt="Hello",
    )

    assert payload == {
        "model": "qwen2.5:1.5b",
        "prompt": "Hello",
        "stream": False,
    }


def test_parse_response():

    client = OllamaClient()

    response = {
        "response": "Hello ScholarOS",
        "model": "qwen2.5:1.5b",
        "prompt_eval_count": 10,
        "eval_count": 20,
    }

    result = client._parse_response(
        response,
    )

    assert isinstance(
        result,
        AIResponse,
    )

    assert (
        result.content
        == "Hello ScholarOS"
    )

    assert (
        result.model
        == "qwen2.5:1.5b"
    )

    assert (
        result.prompt_tokens
        == 10
    )

    assert (
        result.completion_tokens
        == 20
    )

    assert (
        result.total_tokens
        == 30
    )


def test_generate():

    client = OllamaClient()

    client._post = MagicMock(
        return_value={
            "response": "ScholarOS is running.",
            "model": "qwen2.5:1.5b",
            "prompt_eval_count": 8,
            "eval_count": 16,
        }
    )

    result = client.generate(
        model="qwen2.5:1.5b",
        prompt="Hello",
    )

    assert isinstance(
        result,
        AIResponse,
    )

    assert (
        result.content
        == "ScholarOS is running."
    )

    assert (
        result.model
        == "qwen2.5:1.5b"
    )

    assert (
        result.total_tokens
        == 24
    )


def test_generate_calls_post():

    client = OllamaClient()

    client._post = MagicMock(
        return_value={
            "response": "",
            "model": "qwen2.5:1.5b",
            "prompt_eval_count": 0,
            "eval_count": 0,
        }
    )

    client.generate(
        model="qwen2.5:1.5b",
        prompt="Testing",
    )

    client._post.assert_called_once()

    