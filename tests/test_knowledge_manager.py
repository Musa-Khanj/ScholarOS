from scholaros.knowledge.collection import KnowledgeCollection
from scholaros.knowledge.document import KnowledgeDocument
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


def create_manager() -> KnowledgeManager:

    registry = KnowledgeRegistry()

    return KnowledgeManager(
        registry,
    )


def test_manager_register():

    manager = create_manager()

    collection = create_collection()

    manager.register(
        "Research",
        collection,
    )

    assert manager.get(
        "Research",
    ) is collection


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
        == collection
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

    assert manager.installed() == []


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
        == "KnowledgeManager("
        "collections=1)"
    )