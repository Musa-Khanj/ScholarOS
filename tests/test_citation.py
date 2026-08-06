from scholaros.research.citation import (
    Citation,
)


def create_citation() -> Citation:

    return Citation(
        title="ScholarOS Architecture",
        source="ScholarOS Documentation",
    )


def test_title():

    citation = create_citation()

    assert (
        citation.title
        ==
        "ScholarOS Architecture"
    )


def test_source():

    citation = create_citation()

    assert (
        citation.source
        ==
        "ScholarOS Documentation"
    )


def test_url_default():

    citation = create_citation()

    assert (
        citation.url
        is None
    )


def test_authors_default():

    citation = create_citation()

    assert (
        citation.authors
        == []
    )


def test_published_default():

    citation = create_citation()

    assert (
        citation.published
        is None
    )


def test_accessed_default():

    citation = create_citation()

    assert (
        citation.accessed
        is None
    )


def test_id_generated():

    citation = create_citation()

    assert isinstance(
        citation.id,
        str,
    )

    assert (
        len(
            citation.id,
        )
        > 0
    )


def test_unique_ids():

    first = create_citation()

    second = create_citation()

    assert (
        first.id
        != second.id
    )


def test_authors_are_independent():

    first = create_citation()

    second = create_citation()

    first.authors.append(
        "Author",
    )

    assert (
        second.authors
        == []
    )


def test_repr():

    citation = create_citation()

    expected = (
        "Citation("
        f"id='{citation.id}', "
        "title='ScholarOS Architecture'"
        ")"
    )

    assert (
        repr(
            citation,
        )
        == expected
    )