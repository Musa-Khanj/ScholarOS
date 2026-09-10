import tkinter as tk
from unittest.mock import Mock

import pytest

from scholaros.ui.frontend import (
    ScholarOSFrontend,
)
from scholaros.ui.presentation import (
    UIPresentation,
)


@pytest.fixture
def root():

    default_root = getattr(tk, "_default_root", None)
    if default_root is not None:
        try:
            default_root.winfo_exists()
            yield default_root
            return
        except tk.TclError:
            pass

    root = tk.Tk()

    root.withdraw()

    yield root


def create_presentation():

    presentation = Mock(
        spec=UIPresentation,
    )

    presentation.status.return_value = (
        "READY"
    )

    presentation.render_status.return_value = (
        "ScholarOS status: READY"
    )

    presentation.render_info.return_value = (
        "ScholarOS\n"
        "Research: AVAILABLE\n"
        "RAG: AVAILABLE\n"
        "Status: READY"
    )

    return presentation


def create_frontend(
    root,
):

    return ScholarOSFrontend(
        create_presentation(),
        root,
    )


def test_frontend_presentation_property(
    root,
):

    presentation = create_presentation()

    frontend = ScholarOSFrontend(
        presentation,
        root,
    )

    assert (
        frontend.presentation
        is presentation
    )


def test_frontend_root_property(
    root,
):

    frontend = create_frontend(
        root,
    )

    assert frontend.root is root


def test_frontend_refresh(
    root,
):

    presentation = create_presentation()

    frontend = ScholarOSFrontend(
        presentation,
        root,
    )

    frontend.refresh()

    assert (
        frontend._status_var.get()
        == "ScholarOS status: READY"
    )

    assert (
        "Research: AVAILABLE"
        in frontend._info_var.get()
    )

    presentation.render_status.assert_called()


def test_frontend_rag_query(
    root,
):

    presentation = create_presentation()

    presentation.rag_query.return_value = (
        "RAG response"
    )

    frontend = ScholarOSFrontend(
        presentation,
        root,
    )

    frontend._rag_query_var.set(
        "What is ScholarOS?",
    )

    frontend._rag_score_var.set(
        "0.5",
    )

    frontend.run_rag()

    assert (
        frontend._rag_output.get(
            "1.0",
            tk.END,
        ).strip()
        == "RAG response"
    )

    presentation.rag_query.assert_called_once_with(
        "What is ScholarOS?",
        0.5,
    )


def test_frontend_research_build(
    root,
):

    presentation = create_presentation()

    presentation.research_build.return_value = (
        "Built prompt"
    )

    frontend = ScholarOSFrontend(
        presentation,
        root,
    )

    frontend._research_template_var.set(
        "Research {topic}",
    )

    frontend._research_variables_var.set(
        "topic=ScholarOS",
    )

    frontend.build_research()

    assert (
        frontend._research_output.get(
            "1.0",
            tk.END,
        ).strip()
        == "Built prompt"
    )

    presentation.research_build.assert_called_once_with(
        "Research {topic}",
        topic="ScholarOS",
    )


def test_frontend_research_execute(
    root,
):

    presentation = create_presentation()

    presentation.research_execute.return_value = (
        "Research result"
    )

    frontend = ScholarOSFrontend(
        presentation,
        root,
    )

    frontend._research_template_var.set(
        "Research {topic}",
    )

    frontend._research_variables_var.set(
        "topic=ScholarOS",
    )

    frontend.execute_research()

    assert (
        frontend._research_output.get(
            "1.0",
            tk.END,
        ).strip()
        == "Research result"
    )

    presentation.research_execute.assert_called_once_with(
        "Research {topic}",
        topic="ScholarOS",
    )


def test_frontend_parse_variables(
    root,
):

    frontend = create_frontend(
        root,
    )

    frontend._research_variables_var.set(
        "topic=AI, year=2026",
    )

    assert (
        frontend._parse_variables()
        == {
            "topic": "AI",
            "year": "2026",
        }
    )


def test_frontend_parse_empty_variables(
    root,
):

    frontend = create_frontend(
        root,
    )

    frontend._research_variables_var.set(
        "",
    )

    assert (
        frontend._parse_variables()
        == {}
    )


def test_frontend_parse_invalid_variables(
    root,
):

    frontend = create_frontend(
        root,
    )

    frontend._research_variables_var.set(
        "invalid",
    )

    with pytest.raises(
        ValueError,
    ):
        frontend._parse_variables()


def test_frontend_format_result_content():

    result = Mock()

    result.content = (
        "Research answer"
    )

    assert (
        ScholarOSFrontend._format_result(
            result,
        )
        == "Research answer"
    )


def test_frontend_format_result_object():

    result = Mock()

    assert (
        ScholarOSFrontend._format_result(
            result,
        )
        == str(result)
    )


def test_frontend_format_none():

    assert (
        ScholarOSFrontend._format_result(
            None,
        )
        == ""
    )


def test_frontend_repr(
    root,
):

    presentation = create_presentation()

    frontend = ScholarOSFrontend(
        presentation,
        root,
    )

    assert (
        repr(frontend)
        == (
            "ScholarOSFrontend("
            f"presentation={presentation!r}"
            ")"
        )
    )