import pytest

from scholaros.ai.llm import (
    Message,
    MessageRole,
    OllamaLLM,
)


def test_ollama_generate():
    llm = OllamaLLM()

    try:
        response = llm.generate(
            [
                Message(
                    role=MessageRole.USER,
                    content="Reply with exactly one word: ScholarOS",
                )
            ]
        )
    except Exception as exc:
        pytest.skip(f"Ollama server is unavailable: {exc}")

    assert response.content
    assert isinstance(response.content, str)

