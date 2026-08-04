from scholaros.retrieval.collection import (
    RetrievalCollection,
)
from scholaros.retrieval.registry import (
    RetrievalRegistry,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)


def create_collection() -> RetrievalCollection:

    collection = RetrievalCollection()

    collection.add(
        RetrievalResult(
            source="knowledge:paper-001",
            content=(
                "Transformer models "
                "achieve state-of-the-art "
                "performance."
            ),
            score=0.96,
            metadata={
                "title": (
                    "Attention Is All You Need"
                ),
            },
        ),
    )

    return collection


def test_registry_add():

    registry = RetrievalRegistry()

    collection = create_collection()

    registry.add(
        "Research",
        collection,
    )

    assert registry.get(
        "Research",
    ) is collection


def test_registry_get():

    registry = RetrievalRegistry()

    collection = create_collection()

    registry.add(
        "Research",
        collection,
    )

    assert registry.get(
        "Research",
    ) is collection


def test_registry_contains():

    registry = RetrievalRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    assert registry.contains(
        "Research",
    )


def test_registry_remove():

    registry = RetrievalRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    registry.remove(
        "Research",
    )

    assert not registry.contains(
        "Research",
    )


def test_registry_names():

    registry = RetrievalRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    assert registry.names() == [
        "Research",
    ]


def test_registry_values():

    registry = RetrievalRegistry()

    collection = create_collection()

    registry.add(
        "Research",
        collection,
    )

    assert registry.values() == [
        collection,
    ]


def test_registry_items():

    registry = RetrievalRegistry()

    collection = create_collection()

    registry.add(
        "Research",
        collection,
    )

    assert registry.items() == [
        (
            "Research",
            collection,
        ),
    ]


def test_registry_clear():

    registry = RetrievalRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    registry.clear()

    assert len(
        registry,
    ) == 0


def test_registry_repr():

    registry = RetrievalRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    assert (
        repr(
            registry,
        )
        == (
            "RetrievalRegistry("
            "collections=1)"
        )
    )