from unittest.mock import MagicMock

from scholaros.ai.ai_service import AIService
from scholaros.ai.prompt_builder import PromptBuilder
from scholaros.ai.prompt_registry import (
    PromptRegistry,
    PromptTemplate,
)
from scholaros.ai.prompt_session import PromptSession
from scholaros.ai.response import AIResponse
from scholaros.research.pipeline import ResearchPipeline


def create_pipeline():

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
        content="Research Summary",
        model="qwen2.5:1.5b",
    )

    session = PromptSession(
        builder,
        llm,
    )

    service = AIService(
        session,
    )

    return ResearchPipeline(
        service,
    )


def test_build():

    pipeline = create_pipeline()

    prompt = pipeline.build(
        "summary",
        topic="Computer Vision",
    )

    assert (
        prompt
        == "Summarize Computer Vision."
    )


def test_execute():

    pipeline = create_pipeline()

    response = pipeline.execute(
        "summary",
        topic="Computer Vision",
    )

    pipeline.ai.session.llm.generate.assert_called_once_with(
        "Summarize Computer Vision."
    )

    assert (
        response.content
        == "Research Summary"
    )


def test_ai_property():

    pipeline = create_pipeline()

    assert isinstance(
        pipeline.ai,
        AIService,
    )


def test_contains():

    pipeline = create_pipeline()

    assert pipeline.contains(
        "summary"
    )

    assert not pipeline.contains(
        "missing"
    )


def test_repr():

    pipeline = create_pipeline()

    representation = repr(
        pipeline,
    )

    assert "ResearchPipeline" in representation

    assert "AIService" in representation