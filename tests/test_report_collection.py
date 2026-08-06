from scholaros.research.report import (
    Report,
)
from scholaros.research.report_collection import (
    ReportCollection,
)


def create_collection() -> ReportCollection:

    return ReportCollection()


def create_report(
    title: str = "ScholarOS",
) -> Report:

    return Report(
        title=title,
        content="Generated report.",
    )


def test_add():

    collection = create_collection()

    report = create_report()

    collection.add(
        report,
    )

    assert (
        collection.all()
        ==
        [
            report,
        ]
    )


def test_remove():

    collection = create_collection()

    report = create_report()

    collection.add(
        report,
    )

    collection.remove(
        report,
    )

    assert (
        collection.all()
        == []
    )


def test_clear():

    collection = create_collection()

    collection.add(
        create_report(
            "One",
        ),
    )

    collection.add(
        create_report(
            "Two",
        ),
    )

    collection.clear()

    assert (
        collection.all()
        == []
    )


def test_all_returns_copy():

    collection = create_collection()

    report = create_report()

    collection.add(
        report,
    )

    reports = (
        collection.all()
    )

    reports.clear()

    assert (
        len(
            collection,
        )
        == 1
    )


def test_len():

    collection = create_collection()

    collection.add(
        create_report(
            "One",
        ),
    )

    collection.add(
        create_report(
            "Two",
        ),
    )

    assert (
        len(
            collection,
        )
        == 2
    )


def test_iter():

    collection = create_collection()

    first = create_report(
        "One",
    )

    second = create_report(
        "Two",
    )

    collection.add(
        first,
    )

    collection.add(
        second,
    )

    assert (
        list(
            collection,
        )
        ==
        [
            first,
            second,
        ]
    )


def test_contains():

    collection = create_collection()

    report = create_report()

    collection.add(
        report,
    )

    assert (
        report
        in collection
    )


def test_repr():

    collection = create_collection()

    collection.add(
        create_report(),
    )

    assert (
        repr(
            collection,
        )
        ==
        "ReportCollection("
        "size=1"
        ")"
    )