from scholaros.embeddings.collection import (
    EmbeddingCollection,
)
from scholaros.embeddings.manager import (
    EmbeddingManager,
)
from scholaros.embeddings.registry import (
    EmbeddingRegistry,
)


def create_manager() -> EmbeddingManager:

    return EmbeddingManager(
        EmbeddingRegistry(),
    )


def create_collection() -> EmbeddingCollection:

    return EmbeddingCollection()


def test_registry_property():

    manager = create_manager()

    assert isinstance(
        manager.registry,
        EmbeddingRegistry,
    )


def test_register():

    manager = create_manager()

    collection = create_collection()

    manager.register(
        "default",
        collection,
    )

    assert (
        manager.get(
            "default",
        )
        is collection
    )


def test_unregister():

    manager = create_manager()

    collection = create_collection()

    manager.register(
        "default",
        collection,
    )

    manager.unregister(
        "default",
    )

    assert (
        manager.get(
            "default",
        )
        is None
    )


def test_contains():

    manager = create_manager()

    manager.register(
        "default",
        create_collection(),
    )

    assert manager.contains(
        "default",
    )

    assert not manager.contains(
        "unknown",
    )


def test_installed():

    manager = create_manager()

    manager.register(
        "one",
        create_collection(),
    )

    manager.register(
        "two",
        create_collection(),
    )

    assert (
        manager.installed()
        ==
        [
            "one",
            "two",
        ]
    )


def test_values():

    manager = create_manager()

    first = create_collection()

    second = create_collection()

    manager.register(
        "one",
        first,
    )

    manager.register(
        "two",
        second,
    )

    assert (
        manager.values()
        ==
        [
            first,
            second,
        ]
    )


def test_clear():

    manager = create_manager()

    manager.register(
        "one",
        create_collection(),
    )

    manager.register(
        "two",
        create_collection(),
    )

    manager.clear()

    assert (
        len(
            manager.registry,
        )
        == 0
    )


def test_repr():

    manager = create_manager()

    manager.register(
        "default",
        create_collection(),
    )

    assert (
        repr(
            manager,
        )
        ==
        "EmbeddingManager("
        "collections=1)"
    )