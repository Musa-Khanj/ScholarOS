from scholaros.memory.entry import MemoryEntry


def create_entry() -> MemoryEntry:

    return MemoryEntry(
        entry_id="memory-001",
        content="The user prefers IEEE citations.",
        metadata={
            "source": "conversation",
            "author": "user",
        },
    )


def test_entry_id_property():

    entry = create_entry()

    assert entry.entry_id == "memory-001"


def test_content_property():

    entry = create_entry()

    assert (
        entry.content
        == "The user prefers IEEE citations."
    )


def test_metadata_property():

    entry = create_entry()

    assert entry.metadata == {
        "source": "conversation",
        "author": "user",
    }


def test_embedding_defaults_to_none():

    entry = create_entry()

    assert entry.embedding is None


def test_embedding_property():

    entry = MemoryEntry(
        entry_id="memory-001",
        content="Embedding example",
        metadata={},
        embedding=[
            0.1,
            0.2,
            0.3,
        ],
    )

    assert entry.embedding == [
        0.1,
        0.2,
        0.3,
    ]


def test_repr():

    entry = create_entry()

    assert (
        repr(
            entry,
        )
        == "MemoryEntry("
        "entry_id='memory-001', "
        "content='The user prefers IEEE citations.'"
        ")"
    )