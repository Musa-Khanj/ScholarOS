from scholaros.research.citation import (
    Citation,
)
from scholaros.research.report import (
    Report,
)
from scholaros.research.report_manager import (
    ReportManager,
)
from scholaros.research.report_registry import (
    ReportRegistry,
)


def create_manager() -> ReportManager:

    return ReportManager()


def create_citation(
    title: str = "Citation",
) -> Citation:

    return Citation(
        title=title,
        source="ScholarOS Documentation",
    )


def create_report(
    title: str = "ScholarOS",
) -> Report:

    return Report(
        title=title,
        content="Generated report.",
    )


def test_registry_property():

    manager = create_manager()

    assert isinstance(
        manager.registry,
        ReportRegistry,
    )


def test_create():

    manager = create_manager()

    report = manager.create(
        title="ScholarOS",
        content="Generated report.",
    )

    assert isinstance(
        report,
        Report,
    )

    assert (
        report.title
        ==
        "ScholarOS"
    )

    assert (
        report.content
        ==
        "Generated report."
    )

    assert (
        report
        in manager
    )


def test_create_with_all_fields():

    manager = create_manager()

    citation = create_citation()

    report = manager.create(
        title="Research Report",
        content="Research content.",
        citations=[
            citation,
        ],
        created_at="2026-08-06",
    )

    assert (
        report.citations
        ==
        [
            citation,
        ]
    )

    assert (
        report.created_at
        ==
        "2026-08-06"
    )


def test_register():

    manager = create_manager()

    report = create_report()

    manager.register(
        report,
    )

    assert (
        manager.reports()
        ==
        [
            report,
        ]
    )


def test_unregister():

    manager = create_manager()

    report = create_report()

    manager.register(
        report,
    )

    manager.unregister(
        report,
    )

    assert (
        manager.reports()
        == []
    )


def test_clear():

    manager = create_manager()

    manager.register(
        create_report(
            "One",
        ),
    )

    manager.register(
        create_report(
            "Two",
        ),
    )

    manager.clear()

    assert (
        manager.reports()
        == []
    )


def test_reports_returns_copy():

    manager = create_manager()

    report = create_report()

    manager.register(
        report,
    )

    reports = (
        manager.reports()
    )

    reports.clear()

    assert (
        len(
            manager,
        )
        == 1
    )


def test_len():

    manager = create_manager()

    manager.register(
        create_report(
            "One",
        ),
    )

    manager.register(
        create_report(
            "Two",
        ),
    )

    assert (
        len(
            manager,
        )
        == 2
    )


def test_iter():

    manager = create_manager()

    first = create_report(
        "One",
    )

    second = create_report(
        "Two",
    )

    manager.register(
        first,
    )

    manager.register(
        second,
    )

    assert (
        list(
            manager,
        )
        ==
        [
            first,
            second,
        ]
    )


def test_contains():

    manager = create_manager()

    report = create_report()

    manager.register(
        report,
    )

    assert (
        report
        in manager
    )


def test_repr():

    manager = create_manager()

    manager.register(
        create_report(),
    )

    assert (
        repr(
            manager,
        )
        ==
        "ReportManager("
        "size=1"
        ")"
    )