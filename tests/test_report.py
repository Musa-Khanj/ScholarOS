from scholaros.research.citation import (
    Citation,
)
from scholaros.research.report import (
    Report,
)


def create_citation() -> Citation:

    return Citation(
        title="ScholarOS Citation",
        source="ScholarOS Documentation",
    )


def create_report() -> Report:

    return Report(
        title="ScholarOS Report",
        content="This is a generated report.",
    )


def test_title():

    report = create_report()

    assert (
        report.title
        ==
        "ScholarOS Report"
    )


def test_content():

    report = create_report()

    assert (
        report.content
        ==
        "This is a generated report."
    )


def test_citations_default():

    report = create_report()

    assert (
        report.citations
        == []
    )


def test_created_at_default():

    report = create_report()

    assert (
        report.created_at
        is None
    )


def test_id_generated():

    report = create_report()

    assert isinstance(
        report.id,
        str,
    )

    assert (
        len(
            report.id,
        )
        > 0
    )


def test_unique_ids():

    first = create_report()

    second = create_report()

    assert (
        first.id
        != second.id
    )


def test_citations_are_independent():

    first = create_report()

    second = create_report()

    first.citations.append(
        create_citation(),
    )

    assert (
        second.citations
        == []
    )


def test_citations_assignment():

    citation = create_citation()

    report = Report(
        title="Research",
        content="Content",
        citations=[
            citation,
        ],
    )

    assert (
        report.citations
        ==
        [
            citation,
        ]
    )


def test_repr():

    report = create_report()

    expected = (
        "Report("
        f"id='{report.id}', "
        "title='ScholarOS Report'"
        ")"
    )

    assert (
        repr(
            report,
        )
        == expected
    )