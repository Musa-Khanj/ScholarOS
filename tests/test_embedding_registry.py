from scholaros.embeddings.collection import (
    EmbeddingCollection,
)
from scholaros.embeddings.registry import (
    EmbeddingRegistry,
)


def create_collection() -> EmbeddingCollection:

    return EmbeddingCollection()


def test_add():

    registry = EmbeddingRegistry()

    collection = create_collection()

    registry.add(
        "default",
        collection,
    )

    assert (
        registry.get(
            "default",
        )
        is collection
    )


def test_remove():

    registry = EmbeddingRegistry()

    collection = create_collection()

    registry.add(
        "default",
        collection,
    )

    registry.remove(
        "default",
    )

    assert (
        registry.get(
            "default",
        )
        is None
    )


def test_contains():

    registry = EmbeddingRegistry()

    registry.add(
        "default",
        create_collection(),
    )

    assert registry.contains(
        "default",
    )

    assert not registry.contains(
        "unknown",
    )


def test_names():

    registry = EmbeddingRegistry()

    registry.add(
        "one",
        create_collection(),
    )

    registry.add(
        "two",
        create_collection(),
    )

    assert registry.names() == [
        "one",
        "two",
    ]


def test_values():

    registry = EmbeddingRegistry()

    first = create_collection()

    second = create_collection()

    registry.add(
        "one",
        first,
    )

    registry.add(
        "two",
        second,
    )

    assert registry.values() == [
        first,
        second,
    ]


def test_clear():

    registry = EmbeddingRegistry()

    registry.add(
        "one",
        create_collection(),
    )

    registry.add(
        "two",
        create_collection(),
    )

    registry.clear()

    assert len(
        registry,
    ) == 0


def test_len():

    registry = EmbeddingRegistry()

    assert len(
        registry,
    ) == 0

    registry.add(
        "default",
        create_collection(),
    )

    assert len(
        registry,
    ) == 1


def test_repr():

    registry = EmbeddingRegistry()

    registry.add(
        "default",
        create_collection(),
    )

    assert (
        repr(
            registry,
        )
        ==
        "EmbeddingRegistry("
        "collections=1)"
    )