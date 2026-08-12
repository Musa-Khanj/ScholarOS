from scholaros.knowledge.collection import (
    KnowledgeCollection,
)
from scholaros.knowledge.document import (
    KnowledgeDocument,
)
from scholaros.knowledge.loader import (
    KnowledgeLoader,
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


def create_loader() -> KnowledgeLoader:
    """
    Build a knowledge loader
    for testing.
    """

    registry = KnowledgeRegistry()

    manager = KnowledgeManager(
        registry=registry,
    )

    return KnowledgeLoader(
        manager=manager,
    )


def test_loader_load():

    loader = create_loader()

    collection = create_collection()

    loader.load(
        "Research",
        collection,
    )

    assert (
        loader.manager.get(
            "Research",
        )
        is collection
    )


def test_loader_remove():

    loader = create_loader()

    loader.load(
        "Research",
        create_collection(),
    )

    loader.remove(
        "Research",
    )

    assert not loader.manager.contains(
        "Research",
    )


def test_loader_reload():

    loader = create_loader()

    collection = create_collection()

    loader.load(
        "Research",
        collection,
    )

    loader.reload(
        "Research",
        collection,
    )

    assert (
        loader.manager.get(
            "Research",
        )
        is collection
    )


def test_loader_discover():

    loader = create_loader()

    loader.load(
        "Research",
        create_collection(),
    )

    assert (
        loader.discover()
        == (
            "Research",
        )
    )


def test_loader_len():

    loader = create_loader()

    loader.load(
        "Research",
        create_collection(),
    )

    assert (
        len(
            loader,
        )
        == 1
    )


def test_loader_repr():

    loader = create_loader()

    loader.load(
        "Research",
        create_collection(),
    )

    assert (
        repr(
            loader,
        )
        == (
            "KnowledgeLoader("
            "collections=1)"
        )
    )