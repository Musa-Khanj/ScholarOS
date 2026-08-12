from unittest.mock import Mock

import pytest

from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.research.pipeline import ResearchPipeline
from scholaros.ui.application import UIApplication


def create_research() -> ResearchPipeline:

    return Mock(
        spec=ResearchPipeline,
    )


def create_rag() -> RAGPipeline:

    return Mock(
        spec=RAGPipeline,
    )


def test_ui_application_research_property():

    research = create_research()

    application = UIApplication(
        research=research,
    )

    assert application.research is research


def test_ui_application_rag_property():

    rag = create_rag()

    application = UIApplication(
        rag=rag,
    )

    assert application.rag is rag


def test_ui_application_status_ready_with_research():

    application = UIApplication(
        research=create_research(),
    )

    assert application.status() == "READY"


def test_ui_application_status_ready_with_rag():

    application = UIApplication(
        rag=create_rag(),
    )

    assert application.status() == "READY"


def test_ui_application_status_not_configured():

    application = UIApplication()

    assert application.status() == "NOT_CONFIGURED"


def test_ui_application_info():

    application = UIApplication(
        research=create_research(),
        rag=create_rag(),
    )

    assert application.info() == {
        "research": True,
        "rag": True,
        "status": "READY",
    }


def test_ui_application_research_execute():

    research = create_research()

    research.execute.return_value = "result"

    application = UIApplication(
        research=research,
    )

    result = application.research_execute(
        "research",
        topic="ScholarOS",
    )

    assert result == "result"

    research.execute.assert_called_once_with(
        "research",
        topic="ScholarOS",
    )


def test_ui_application_research_build():

    research = create_research()

    research.build.return_value = (
        "Built research prompt."
    )

    application = UIApplication(
        research=research,
    )

    result = application.research_build(
        "research",
        topic="ScholarOS",
    )

    assert (
        result
        == "Built research prompt."
    )

    research.build.assert_called_once_with(
        "research",
        topic="ScholarOS",
    )


def test_ui_application_research_contains():

    research = create_research()

    research.contains.return_value = True

    application = UIApplication(
        research=research,
    )

    assert application.research_contains(
        "research",
    )

    research.contains.assert_called_once_with(
        "research",
    )


def test_ui_application_research_requires_pipeline():

    application = UIApplication()

    with pytest.raises(
        RuntimeError,
        match="Research pipeline is not configured.",
    ):
        application.research_execute(
            "research",
        )


def test_ui_application_research_build_requires_pipeline():

    application = UIApplication()

    with pytest.raises(
        RuntimeError,
        match="Research pipeline is not configured.",
    ):
        application.research_build(
            "research",
        )


def test_ui_application_research_contains_requires_pipeline():

    application = UIApplication()

    with pytest.raises(
        RuntimeError,
        match="Research pipeline is not configured.",
    ):
        application.research_contains(
            "research",
        )


def test_ui_application_rag_run():

    rag = create_rag()

    response = Mock(
        spec=RAGResponse,
    )

    rag.run.return_value = response

    application = UIApplication(
        rag=rag,
    )

    request = Mock()

    result = application.rag_run(
        request,
    )

    assert result is response

    rag.run.assert_called_once_with(
        request,
    )


def test_ui_application_rag_query():

    rag = create_rag()

    response = Mock(
        spec=RAGResponse,
    )

    rag.run.return_value = response

    application = UIApplication(
        rag=rag,
    )

    result = application.rag_query(
        "What is ScholarOS?",
        0.5,
    )

    assert result is response

    request = rag.run.call_args.args[0]

    assert request.query == (
        "What is ScholarOS?"
    )

    assert request.minimum_score == 0.5


def test_ui_application_rag_requires_pipeline():

    application = UIApplication()

    with pytest.raises(
        RuntimeError,
        match="RAG pipeline is not configured.",
    ):
        application.rag_query(
            "What is ScholarOS?",
        )


def test_ui_application_repr():

    application = UIApplication(
        research=create_research(),
        rag=create_rag(),
    )

    assert (
        repr(application)
        == (
            "UIApplication("
            "research=True, "
            "rag=True"
            ")"
        )
    )