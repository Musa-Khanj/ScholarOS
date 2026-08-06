from scholaros.research.citation import (
    Citation,
)
from scholaros.research.citation_collection import (
    CitationCollection,
)
from scholaros.research.citation_registry import (
    CitationRegistry,
)


def create_registry() -> CitationRegistry:

    return CitationRegistry()


def create_citation(
    title: str = "ScholarOS",
) -> Citation:

    return Citation(
        title=title,
        source="ScholarOS Documentation",
    )


def test_collection_property():

    registry = create_registry()

    assert isinstance(
        registry.collection,
        CitationCollection,
    )


def test_register():

    registry = create_registry()

    citation = create_citation()

    registry.register(
        citation,
    )

    assert (
        registry.citations()
        ==
        [
            citation,
        ]
    )


def test_unregister():

    registry = create_registry()

    citation = create_citation()

    registry.register(
        citation,
    )

    registry.unregister(
        citation,
    )

    assert (
        registry.citations()
        == []
    )


def test_clear():

    registry = create_registry()

    registry.register(
        create_citation(
            "One",
        ),
    )

    registry.register(
        create_citation(
            "Two",
        ),
    )

    registry.clear()

    assert (
        registry.citations()
        == []
    )


def test_citations_returns_copy():

    registry = create_registry()

    citation = create_citation()

    registry.register(
        citation,
    )

    citations = (
        registry.citations()
    )

    citations.clear()

    assert (
        len(
            registry,
        )
        == 1
    )


def test_len():

    registry = create_registry()

    registry.register(
        create_citation(
            "One",
        ),
    )

    registry.register(
        create_citation(
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

    first = create_citation(
        "One",
    )

    second = create_citation(
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

    citation = create_citation()

    registry.register(
        citation,
    )

    assert (
        citation
        in registry
    )


def test_repr():

    registry = create_registry()

    registry.register(
        create_citation(),
    )

    assert (
        repr(
            registry,
        )
        ==
        "CitationRegistry("
        "size=1"
        ")"
    )