from scholaros.research.citation import (
    Citation,
)
from scholaros.research.citation_collection import (
    CitationCollection,
)


def create_collection() -> CitationCollection:

    return CitationCollection()


def create_citation(
    title: str = "ScholarOS",
) -> Citation:

    return Citation(
        title=title,
        source="ScholarOS Documentation",
    )


def test_add():

    collection = create_collection()

    citation = create_citation()

    collection.add(
        citation,
    )

    assert (
        collection.all()
        ==
        [
            citation,
        ]
    )


def test_remove():

    collection = create_collection()

    citation = create_citation()

    collection.add(
        citation,
    )

    collection.remove(
        citation,
    )

    assert (
        collection.all()
        == []
    )


def test_clear():

    collection = create_collection()

    collection.add(
        create_citation(
            "One",
        ),
    )

    collection.add(
        create_citation(
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

    citation = create_citation()

    collection.add(
        citation,
    )

    citations = (
        collection.all()
    )

    citations.clear()

    assert (
        len(
            collection,
        )
        == 1
    )


def test_len():

    collection = create_collection()

    collection.add(
        create_citation(
            "One",
        ),
    )

    collection.add(
        create_citation(
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

    first = create_citation(
        "One",
    )

    second = create_citation(
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

    citation = create_citation()

    collection.add(
        citation,
    )

    assert (
        citation
        in collection
    )


def test_repr():

    collection = create_collection()

    collection.add(
        create_citation(),
    )

    assert (
        repr(
            collection,
        )
        ==
        "CitationCollection("
        "size=1"
        ")"
    )