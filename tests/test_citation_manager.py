from scholaros.research.citation import (
    Citation,
)
from scholaros.research.citation_manager import (
    CitationManager,
)
from scholaros.research.citation_registry import (
    CitationRegistry,
)


def create_manager() -> CitationManager:

    return CitationManager()


def create_citation(
    title: str = "ScholarOS",
) -> Citation:

    return Citation(
        title=title,
        source="ScholarOS Documentation",
    )


def test_registry_property():

    manager = create_manager()

    assert isinstance(
        manager.registry,
        CitationRegistry,
    )


def test_create():

    manager = create_manager()

    citation = manager.create(
        title="ScholarOS",
        source="ScholarOS Documentation",
    )

    assert isinstance(
        citation,
        Citation,
    )

    assert (
        citation.title
        ==
        "ScholarOS"
    )

    assert (
        citation.source
        ==
        "ScholarOS Documentation"
    )

    assert (
        citation
        in manager
    )


def test_create_with_all_fields():

    manager = create_manager()

    citation = manager.create(
        title="Research Paper",
        source="IEEE",
        url="https://example.com",
        authors=[
            "Alice",
            "Bob",
        ],
        published="2026",
        accessed="2026-08-05",
    )

    assert (
        citation.url
        ==
        "https://example.com"
    )

    assert (
        citation.authors
        ==
        [
            "Alice",
            "Bob",
        ]
    )

    assert (
        citation.published
        ==
        "2026"
    )

    assert (
        citation.accessed
        ==
        "2026-08-05"
    )


def test_register():

    manager = create_manager()

    citation = create_citation()

    manager.register(
        citation,
    )

    assert (
        manager.citations()
        ==
        [
            citation,
        ]
    )


def test_unregister():

    manager = create_manager()

    citation = create_citation()

    manager.register(
        citation,
    )

    manager.unregister(
        citation,
    )

    assert (
        manager.citations()
        == []
    )


def test_clear():

    manager = create_manager()

    manager.register(
        create_citation(
            "One",
        ),
    )

    manager.register(
        create_citation(
            "Two",
        ),
    )

    manager.clear()

    assert (
        manager.citations()
        == []
    )


def test_citations_returns_copy():

    manager = create_manager()

    citation = create_citation()

    manager.register(
        citation,
    )

    citations = (
        manager.citations()
    )

    citations.clear()

    assert (
        len(
            manager,
        )
        == 1
    )


def test_len():

    manager = create_manager()

    manager.register(
        create_citation(
            "One",
        ),
    )

    manager.register(
        create_citation(
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

    first = create_citation(
        "One",
    )

    second = create_citation(
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

    citation = create_citation()

    manager.register(
        citation,
    )

    assert (
        citation
        in manager
    )


def test_repr():

    manager = create_manager()

    manager.register(
        create_citation(),
    )

    assert (
        repr(
            manager,
        )
        ==
        "CitationManager("
        "size=1"
        ")"
    )