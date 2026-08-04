from scholaros.knowledge.collection import KnowledgeCollection
from scholaros.knowledge.document import KnowledgeDocument
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


def test_registry_add():

    registry = KnowledgeRegistry()

    collection = create_collection()

    registry.add(
        "Research",
        collection,
    )

    assert registry.get(
        "Research",
    ) is collection


def test_registry_get():

    registry = KnowledgeRegistry()

    collection = create_collection()

    registry.add(
        "Research",
        collection,
    )

    assert (
        registry.get(
            "Research",
        )
        == collection
    )


def test_registry_contains():

    registry = KnowledgeRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    assert registry.contains(
        "Research",
    )


def test_registry_remove():

    registry = KnowledgeRegistry()

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

    registry = KnowledgeRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    assert registry.names() == [
        "Research",
    ]


def test_registry_values():

    registry = KnowledgeRegistry()

    collection = create_collection()

    registry.add(
        "Research",
        collection,
    )

    assert registry.values() == [
        collection,
    ]


def test_registry_items():

    registry = KnowledgeRegistry()

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

    registry = KnowledgeRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    registry.clear()

    assert len(
        registry,
    ) == 0


def test_registry_repr():

    registry = KnowledgeRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    assert (
        repr(
            registry,
        )
        == "KnowledgeRegistry("
        "collections=1)"
    )