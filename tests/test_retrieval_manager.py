from scholaros.retrieval.collection import (
    RetrievalCollection,
)
from scholaros.retrieval.manager import (
    RetrievalManager,
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


def create_manager() -> RetrievalManager:

    registry = RetrievalRegistry()

    return RetrievalManager(
        registry,
    )


def test_manager_register():

    manager = create_manager()

    collection = create_collection()

    manager.register(
        "Research",
        collection,
    )

    assert (
        manager.get(
            "Research",
        )
        is collection
    )


def test_manager_unregister():

    manager = create_manager()

    manager.register(
        "Research",
        create_collection(),
    )

    manager.unregister(
        "Research",
    )

    assert not manager.contains(
        "Research",
    )


def test_manager_get():

    manager = create_manager()

    collection = create_collection()

    manager.register(
        "Research",
        collection,
    )

    assert (
        manager.get(
            "Research",
        )
        is collection
    )


def test_manager_contains():

    manager = create_manager()

    manager.register(
        "Research",
        create_collection(),
    )

    assert manager.contains(
        "Research",
    )


def test_manager_installed():

    manager = create_manager()

    manager.register(
        "Research",
        create_collection(),
    )

    assert manager.installed() == [
        "Research",
    ]


def test_manager_clear():

    manager = create_manager()

    manager.register(
        "Research",
        create_collection(),
    )

    manager.clear()

    assert (
        manager.installed()
        == []
    )


def test_manager_repr():

    manager = create_manager()

    manager.register(
        "Research",
        create_collection(),
    )

    assert (
        repr(
            manager,
        )
        == (
            "RetrievalManager("
            "collections=1)"
        )
    )