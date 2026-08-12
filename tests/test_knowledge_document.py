from scholaros.knowledge.document import (
    KnowledgeDocument,
)
from scholaros.knowledge.metadata import (
    KnowledgeMetadata,
)


def create_document() -> KnowledgeDocument:

    metadata = KnowledgeMetadata(
        author="John Doe",
        source="Internal",
        language="en",
        version="1.0",
        tags=(
            "design",
            "architecture",
        ),
    )

    return KnowledgeDocument(
        identifier="doc-001",
        title="ScholarOS Design",
        content="Knowledge architecture.",
        metadata=metadata,
    )


def test_identifier_property():

    document = create_document()

    assert (
        document.identifier
        == "doc-001"
    )


def test_title_property():

    document = create_document()

    assert (
        document.title
        == "ScholarOS Design"
    )


def test_content_property():

    document = create_document()

    assert (
        document.content
        == "Knowledge architecture."
    )


def test_metadata_property():

    document = create_document()

    assert (
        document.metadata
        is not None
    )


def test_repr():

    document = create_document()

    assert (
        repr(
            document,
        )
        == (
            "KnowledgeDocument("
            "identifier='doc-001', "
            "title='ScholarOS Design'"
            ")"
        )
    )