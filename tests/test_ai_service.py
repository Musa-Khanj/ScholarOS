from unittest.mock import MagicMock

from scholaros.ai.ai_service import AIService
from scholaros.ai.prompt_builder import PromptBuilder
from scholaros.ai.prompt_registry import (
    PromptRegistry,
    PromptTemplate,
)
from scholaros.ai.prompt_session import PromptSession
from scholaros.ai.response import AIResponse


def create_service():

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
        content="ScholarOS Summary",
        model="qwen2.5:1.5b",
    )

    session = PromptSession(
        builder,
        llm,
    )

    return AIService(
        session,
    )


def test_build():

    service = create_service()

    prompt = service.build(
        "summary",
        topic="Artificial Intelligence",
    )

    assert (
        prompt
        == "Summarize Artificial Intelligence."
    )


def test_execute():

    service = create_service()

    response = service.execute(
        "summary",
        topic="Artificial Intelligence",
    )

    service.session.llm.generate.assert_called_once_with(
        "Summarize Artificial Intelligence."
    )

    assert (
        response.content
        == "ScholarOS Summary"
    )


def test_session_property():

    service = create_service()

    assert isinstance(
        service.session,
        PromptSession,
    )


def test_contains():

    service = create_service()

    assert service.contains(
        "summary"
    )

    assert not service.contains(
        "missing"
    )


def test_repr():

    service = create_service()

    representation = repr(
        service,
    )

    assert "AIService" in representation

    assert "PromptSession" in representation