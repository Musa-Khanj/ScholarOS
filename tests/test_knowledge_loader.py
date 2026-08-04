from scholaros.knowledge.collection import KnowledgeCollection
from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.loader import KnowledgeLoader
from scholaros.knowledge.manager import KnowledgeManager
from scholaros.knowledge.metadata import KnowledgeMetadata
from scholaros.knowledge.registry import KnowledgeRegistry


def create_collection() -> KnowledgeCollection:

    metadata = KnowledgeMetadata(
        author="Musa Khan",
        source="ScholarOS",
        language="English",
        version="1.0",
        tags=[
            "AI",
            "Knowledge",
        ],
    )

    document = KnowledgeDocument(
        document_id="doc-001",
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

    registry = KnowledgeRegistry()

    manager = KnowledgeManager(
        registry,
    )

    return KnowledgeLoader(
        manager,
    )


def test_loader_load():

    loader = create_loader()

    collection = create_collection()

    loader.load(
        "Research",
        collection,
    )

    assert loader.manager.get(
        "Research",
    ) is collection


def test_loader_unload():

    loader = create_loader()

    loader.load(
        "Research",
        create_collection(),
    )

    loader.unload(
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

    assert loader.manager.get(
        "Research",
    ) is collection


def test_loader_discover():

    loader = create_loader()

    loader.load(
        "Research",
        create_collection(),
    )

    assert loader.discover() == [
        "Research",
    ]


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
        == "KnowledgeLoader("
        "collections=1)"
    )