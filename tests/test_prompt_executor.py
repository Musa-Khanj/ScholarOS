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

    response = executor.execute(
        prompt
    )

    assert response.content
    assert isinstance(
        response.content,
        str,
    )