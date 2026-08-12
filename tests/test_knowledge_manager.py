from scholaros.knowledge.collection import (
    KnowledgeCollection,
)
from scholaros.knowledge.document import (
    KnowledgeDocument,
)
from scholaros.knowledge.manager import (
    KnowledgeManager,
)
from scholaros.knowledge.metadata import (
    KnowledgeMetadata,
)
from scholaros.knowledge.registry import (
    KnowledgeRegistry,
)


def create_collection() -> KnowledgeCollection:
    """
    Build a small knowledge
    collection for testing.
    """

    metadata = KnowledgeMetadata(
        author="Musa Khan",
        source="ScholarOS",
        language="English",
        version="1.0",
        tags=(
            "AI",
            "Knowledge",
        ),
    )

    document = KnowledgeDocument(
        identifier="doc-001",
        title="ScholarOS Design",
        content="Knowledge architecture.",
        metadata=metadata,
    )

    collection = KnowledgeCollection()

    collection.add(
        document,
    )

    return collection


def test_manager_init_default():

    manager = KnowledgeManager()

    assert isinstance(
        manager.registry,
        KnowledgeRegistry,
    )


def test_manager_init_custom():

    registry = KnowledgeRegistry()

    manager = KnowledgeManager(
        registry=registry,
    )

    assert (
        manager.registry
        is registry
    )


def test_manager_add():

    manager = KnowledgeManager()

    collection = create_collection()

    manager.add(
        "Research",
        collection,
    )

    assert (
        manager.get(
            "Research",
        )
        is collection
    )


def test_manager_add_duplicate():

    manager = KnowledgeManager()

    manager.add(
        "Research",
        create_collection(),
    )

    try:
        manager.add(
            "Research",
            create_collection(),
        )

    except ValueError:
        return

    raise AssertionError(
        "Duplicate registration "
        "did not raise ValueError."
    )


def test_manager_get():

    manager = KnowledgeManager()

    collection = create_collection()

    manager.add(
        "Research",
        collection,
    )

    assert (
        manager.get(
            "Research",
        )
        == collection
    )


def test_manager_get_unknown():

    manager = KnowledgeManager()

    try:
        manager.get(
            "Missing",
        )

    except KeyError:
        return

    raise AssertionError(
        "Unknown lookup did not "
        "raise KeyError."
    )


def test_manager_contains():

    manager = KnowledgeManager()

    manager.add(
        "Research",
        create_collection(),
    )

    assert manager.contains(
        "Research",
    )


def test_manager_remove():

    manager = KnowledgeManager()

    manager.add(
        "Research",
        create_collection(),
    )

    manager.remove(
        "Research",
    )

    assert not manager.contains(
        "Research",
    )


def test_manager_names():

    manager = KnowledgeManager()

    manager.add(
        "Research",
        create_collection(),
    )

    assert (
        manager.names()
        == (
            "Research",
        )
    )


def test_manager_clear():

    manager = KnowledgeManager()

    manager.add(
        "Research",
        create_collection(),
    )

    manager.clear()

    assert (
        len(
            manager,
        )
        == 0
    )


def test_manager_len():

    manager = KnowledgeManager()

    manager.add(
        "Research",
        create_collection(),
    )

    assert (
        len(
            manager,
        )
        == 1
    )


def test_manager_repr():

    manager = KnowledgeManager()

    manager.add(
        "Research",
        create_collection(),
    )

    assert (
        repr(
            manager,
        )
        == (
            "KnowledgeManager("
            "collections=1)"
        )
    )