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
from scholaros.research.task import ResearchTask


def create_task():

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
        content="Research Complete",
        model="qwen2.5:1.5b",
    )

    session = PromptSession(
        builder,
        llm,
    )

    service = AIService(
        session,
    )

    pipeline = ResearchPipeline(
        service,
    )

    return ResearchTask(
        pipeline,
        "summary",
    )


def test_build():

    task = create_task()

    prompt = task.build(
        topic="Machine Learning",
    )

    assert (
        prompt
        == "Summarize Machine Learning."
    )


def test_execute():

    task = create_task()

    response = task.execute(
        topic="Machine Learning",
    )

    task.pipeline.ai.session.llm.generate.assert_called_once_with(
        "Summarize Machine Learning."
    )

    assert (
        response.content
        == "Research Complete"
    )


def test_pipeline_property():

    task = create_task()

    assert isinstance(
        task.pipeline,
        ResearchPipeline,
    )


def test_template_property():

    task = create_task()

    assert (
        task.template
        == "summary"
    )


def test_exists():

    task = create_task()

    assert task.exists()


def test_repr():

    task = create_task()

    representation = repr(
        task,
    )

    assert "ResearchTask" in representation

    assert "summary" in representation