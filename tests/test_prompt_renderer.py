import pytest

from scholaros.ai.llm import MessageRole
from scholaros.ai.prompt import PromptRenderer


def test_render_prompt():

    renderer = PromptRenderer()

    prompt = renderer.render(
        "Hello {{name}}!",
        name="ScholarOS",
    )

    assert (
        prompt.messages[0].content
        == "Hello ScholarOS!"
    )


def test_render_role():

    renderer = PromptRenderer()

    prompt = renderer.render(
        "System prompt",
        role=MessageRole.SYSTEM,
    )

    assert (
        prompt.messages[0].role
        == MessageRole.SYSTEM
    )


def test_missing_variable():

    renderer = PromptRenderer()

    with pytest.raises(ValueError):
        renderer.render(
            "Hello {{name}}"
        )