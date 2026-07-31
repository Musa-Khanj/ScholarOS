from unittest.mock import MagicMock

from scholaros.agents import ResearchAgent
from scholaros.ai.ai_service import AIService
from scholaros.ai.prompt_builder import PromptBuilder
from scholaros.ai.prompt_registry import (
    PromptRegistry,
    PromptTemplate,
)
from scholaros.ai.prompt_session import PromptSession
from scholaros.ai.response import AIResponse
from scholaros.research.pipeline import ResearchPipeline


def create_agent() -> ResearchAgent:

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

    pipeline = ResearchPipeline(
        service,
    )

    return ResearchAgent(
        pipeline,
    )


def test_name_property():

    agent = create_agent()

    assert (
        agent.name
        == "Research Agent"
    )


def test_description_property():

    agent = create_agent()

    assert (
        agent.description
        == "Executes research-oriented tasks."
    )


def test_version_property():

    agent = create_agent()

    assert (
        agent.version
        == "1.0"
    )


def test_pipeline_property():

    agent = create_agent()

    assert isinstance(
        agent.pipeline,
        ResearchPipeline,
    )


def test_execute():

    agent = create_agent()

    try:
        agent.execute()
    except NotImplementedError:
        pass
    else:
        assert False


def test_repr():

    agent = create_agent()

    assert (
        repr(agent)
        == (
            "ResearchAgent("
            "name='Research Agent', "
            "version='1.0'"
            ")"
        )
    )