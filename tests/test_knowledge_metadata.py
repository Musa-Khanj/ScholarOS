from scholaros.knowledge.metadata import KnowledgeMetadata


def create_metadata() -> KnowledgeMetadata:

    return KnowledgeMetadata(
        author="Musa Khan",
        source="ScholarOS",
        language="English",
        version="1.0",
        tags=[
            "AI",
            "Knowledge",
            "Research",
        ],
    )


def test_author_property():

    metadata = create_metadata()

    assert metadata.author == "Musa Khan"


def test_source_property():

    metadata = create_metadata()

    assert metadata.source == "ScholarOS"


def test_language_property():

    metadata = create_metadata()

    assert metadata.language == "English"


def test_version_property():

    metadata = create_metadata()

    assert metadata.version == "1.0"


def test_tags_property():

    metadata = create_metadata()

    assert metadata.tags == [
        "AI",
        "Knowledge",
        "Research",
    ]


def test_repr():

    metadata = create_metadata()

    assert (
        repr(metadata)
        == (
            "KnowledgeMetadata("
            "author='Musa Khan', "
            "source='ScholarOS', "
            "language='English', "
            "version='1.0', "
            "tags=['AI', 'Knowledge', 'Research']"
            ")"
        )
    )