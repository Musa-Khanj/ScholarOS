from unittest.mock import MagicMock

from scholaros.ai.prompt_builder import (
    PromptBuilder,
)
from scholaros.ai.prompt_registry import (
    PromptRegistry,
    PromptTemplate,
)
from scholaros.ai.prompt_session import (
    PromptSession,
)
from scholaros.ai.response import (
    AIResponse,
)


def create_session():

    registry = PromptRegistry()

    registry.register(
        PromptTemplate(
            name="summary",
            template="Summarize {topic}.",
        )
    )

    builder = PromptBuilder(
        registry,
    )

    llm = MagicMock()

    llm.model = "qwen2.5:1.5b"

    llm.generate.return_value = AIResponse(
        content="Artificial Intelligence Summary",
        model="qwen2.5:1.5b",
    )

    return PromptSession(
        builder,
        llm,
    )


def test_build():

    session = create_session()

    prompt = session.build(
        "summary",
        topic="Artificial Intelligence",
    )

    assert (
        prompt
        == "Summarize Artificial Intelligence."
    )


def test_execute():

    session = create_session()

    response = session.execute(
        "summary",
        topic="Artificial Intelligence",
    )

    session.llm.generate.assert_called_once_with(
        "Summarize Artificial Intelligence."
    )

    assert (
        response.content
        == "Artificial Intelligence Summary"
    )


def test_builder_property():

    session = create_session()

    assert isinstance(
        session.builder,
        PromptBuilder,
    )


def test_llm_property():

    session = create_session()

    assert (
        session.llm.model
        == "qwen2.5:1.5b"
    )


def test_repr():

    session = create_session()

    representation = repr(session)

    assert "PromptSession" in representation

    assert "templates=1" in representation

    assert "qwen2.5:1.5b" in representation