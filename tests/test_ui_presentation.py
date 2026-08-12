from unittest.mock import Mock

from scholaros.ui.application import (
    UIApplication,
)
from scholaros.ui.presentation import (
    UIPresentation,
)


def create_application() -> UIApplication:

    application = Mock(
        spec=UIApplication,
    )

    return application


def create_presentation() -> UIPresentation:

    return UIPresentation(
        create_application(),
    )


def test_presentation_application_property():

    application = create_application()

    presentation = UIPresentation(
        application,
    )

    assert (
        presentation.application
        is application
    )


def test_presentation_status():

    application = create_application()

    application.status.return_value = (
        "READY"
    )

    presentation = UIPresentation(
        application,
    )

    assert (
        presentation.status()
        == "READY"
    )

    application.status.assert_called_once_with()


def test_presentation_info():

    application = create_application()

    application.info.return_value = {
        "research": True,
        "rag": True,
        "status": "READY",
    }

    presentation = UIPresentation(
        application,
    )

    assert presentation.info() == {
        "research": True,
        "rag": True,
        "status": "READY",
    }

    application.info.assert_called_once_with()


def test_presentation_research_execute():

    application = create_application()

    application.research_execute.return_value = (
        "result"
    )

    presentation = UIPresentation(
        application,
    )

    result = presentation.research_execute(
        "research",
        topic="ScholarOS",
    )

    assert result == "result"

    application.research_execute.assert_called_once_with(
        "research",
        topic="ScholarOS",
    )


def test_presentation_research_build():

    application = create_application()

    application.research_build.return_value = (
        "Built research prompt."
    )

    presentation = UIPresentation(
        application,
    )

    result = presentation.research_build(
        "research",
        topic="ScholarOS",
    )

    assert (
        result
        == "Built research prompt."
    )

    application.research_build.assert_called_once_with(
        "research",
        topic="ScholarOS",
    )


def test_presentation_research_contains():

    application = create_application()

    application.research_contains.return_value = (
        True
    )

    presentation = UIPresentation(
        application,
    )

    assert presentation.research_contains(
        "research",
    )

    application.research_contains.assert_called_once_with(
        "research",
    )


def test_presentation_rag_query():

    application = create_application()

    response = Mock()

    application.rag_query.return_value = (
        response
    )

    presentation = UIPresentation(
        application,
    )

    result = presentation.rag_query(
        "What is ScholarOS?",
        0.5,
    )

    assert result is response

    application.rag_query.assert_called_once_with(
        "What is ScholarOS?",
        0.5,
    )


def test_presentation_render_status():

    application = create_application()

    application.status.return_value = (
        "READY"
    )

    presentation = UIPresentation(
        application,
    )

    assert (
        presentation.render_status()
        == "ScholarOS status: READY"
    )


def test_presentation_render_info():

    application = create_application()

    application.info.return_value = {
        "research": True,
        "rag": False,
        "status": "READY",
    }

    presentation = UIPresentation(
        application,
    )

    assert (
        presentation.render_info()
        == (
            "ScholarOS\n"
            "Research: AVAILABLE\n"
            "RAG: UNAVAILABLE\n"
            "Status: READY"
        )
    )


def test_presentation_repr():

    application = create_application()

    presentation = UIPresentation(
        application,
    )

    assert (
        repr(presentation)
        == (
            "UIPresentation("
            f"application={application!r}"
            ")"
        )
    )