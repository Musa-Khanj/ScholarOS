import pytest

from scholaros.ai.prompt import (
    PromptExecutor,
    ResearchAssistantTemplate,
)
from scholaros.ai.providers import register_ai_services
from scholaros.container import Container


def test_prompt_executor():

    container = Container()

    register_ai_services(container)

    executor = container.resolve(
        PromptExecutor
    )

    prompt = ResearchAssistantTemplate().render(
        topic="Artificial Intelligence"
    )

    try:
        response = executor.execute(
            prompt
        )
    except Exception as exc:
        pytest.skip(f"Ollama server is unavailable: {exc}")

    assert response.content
    assert isinstance(
        response.content,
        str,
    )
