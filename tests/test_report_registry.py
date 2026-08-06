from scholaros.research.report import (
    Report,
)
from scholaros.research.report_collection import (
    ReportCollection,
)
from scholaros.research.report_registry import (
    ReportRegistry,
)


def create_registry() -> ReportRegistry:

    return ReportRegistry()


def create_report(
    title: str = "ScholarOS",
) -> Report:

    return Report(
        title=title,
        content="Generated report.",
    )


def test_collection_property():

    registry = create_registry()

    assert isinstance(
        registry.collection,
        ReportCollection,
    )


def test_register():

    registry = create_registry()

    report = create_report()

    registry.register(
        report,
    )

    assert (
        registry.reports()
        ==
        [
            report,
        ]
    )


def test_unregister():

    registry = create_registry()

    report = create_report()

    registry.register(
        report,
    )

    registry.unregister(
        report,
    )

    assert (
        registry.reports()
        == []
    )


def test_clear():

    registry = create_registry()

    registry.register(
        create_report(
            "One",
        ),
    )

    registry.register(
        create_report(
            "Two",
        ),
    )

    registry.clear()

    assert (
        registry.reports()
        == []
    )


def test_reports_returns_copy():

    registry = create_registry()

    report = create_report()

    registry.register(
        report,
    )

    reports = (
        registry.reports()
    )

    reports.clear()

    assert (
        len(
            registry,
        )
        == 1
    )


def test_len():

    registry = create_registry()

    registry.register(
        create_report(
            "One",
        ),
    )

    registry.register(
        create_report(
            "Two",
        ),
    )

    assert (
        len(
            registry,
        )
        == 2
    )


def test_iter():

    registry = create_registry()

    first = create_report(
        "One",
    )

    second = create_report(
        "Two",
    )

    registry.register(
        first,
    )

    registry.register(
        second,
    )

    assert (
        list(
            registry,
        )
        ==
        [
            first,
            second,
        ]
    )


def test_contains():

    registry = create_registry()

    report = create_report()

    registry.register(
        report,
    )

    assert (
        report
        in registry
    )


def test_repr():

    registry = create_registry()

    registry.register(
        create_report(),
    )

    assert (
        repr(
            registry,
        )
        ==
        "ReportRegistry("
        "size=1"
        ")"
    )