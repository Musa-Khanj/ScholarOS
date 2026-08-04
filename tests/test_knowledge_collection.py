from scholaros.knowledge.collection import KnowledgeCollection
from scholaros.knowledge.document import KnowledgeDocument
from scholaros.knowledge.metadata import KnowledgeMetadata


def create_document() -> KnowledgeDocument:

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

    return KnowledgeDocument(
        document_id="doc-001",
        title="ScholarOS Design",
        content="Knowledge architecture.",
        metadata=metadata,
    )


def test_collection_add():

    collection = KnowledgeCollection()

    document = create_document()

    collection.add(
        document,
    )

    assert collection.get(
        "doc-001",
    ) is document


def test_collection_get():

    collection = KnowledgeCollection()

    document = create_document()

    collection.add(
        document,
    )

    assert (
        collection.get(
            "doc-001",
        )
        == document
    )


def test_collection_contains():

    collection = KnowledgeCollection()

    collection.add(
        create_document(),
    )

    assert collection.contains(
        "doc-001",
    )


def test_collection_remove():

    collection = KnowledgeCollection()

    collection.add(
        create_document(),
    )

    collection.remove(
        "doc-001",
    )

    assert not collection.contains(
        "doc-001",
    )


def test_collection_ids():

    collection = KnowledgeCollection()

    collection.add(
        create_document(),
    )

    assert collection.ids() == [
        "doc-001",
    ]


def test_collection_values():

    collection = KnowledgeCollection()

    document = create_document()

    collection.add(
        document,
    )

    assert collection.values() == [
        document,
    ]


def test_collection_items():

    collection = KnowledgeCollection()

    document = create_document()

    collection.add(
        document,
    )

    assert collection.items() == [
        (
            "doc-001",
            document,
        ),
    ]


def test_collection_clear():

    collection = KnowledgeCollection()

    collection.add(
        create_document(),
    )

    collection.clear()

    assert len(
        collection,
    ) == 0


def test_collection_repr():

    collection = KnowledgeCollection()

    collection.add(
        create_document(),
    )

    assert (
        repr(
            collection,
        )
        == "KnowledgeCollection("
        "documents=1)"
    )