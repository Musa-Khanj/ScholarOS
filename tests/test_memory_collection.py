from scholaros.memory.collection import MemoryCollection
from scholaros.memory.entry import MemoryEntry


def create_entry() -> MemoryEntry:

    return MemoryEntry(
        entry_id="memory-001",
        content="The user prefers IEEE citations.",
        metadata={
            "source": "conversation",
        },
    )


def test_collection_add():

    collection = MemoryCollection()

    entry = create_entry()

    collection.add(
        entry,
    )

    assert collection.get(
        "memory-001",
    ) is entry


def test_collection_get():

    collection = MemoryCollection()

    entry = create_entry()

    collection.add(
        entry,
    )

    assert collection.get(
        "memory-001",
    ) is entry


def test_collection_contains():

    collection = MemoryCollection()

    collection.add(
        create_entry(),
    )

    assert collection.contains(
        "memory-001",
    )


def test_collection_remove():

    collection = MemoryCollection()

    collection.add(
        create_entry(),
    )

    collection.remove(
        "memory-001",
    )

    assert not collection.contains(
        "memory-001",
    )


def test_collection_entries():

    collection = MemoryCollection()

    entry = create_entry()

    collection.add(
        entry,
    )

    assert collection.entries() == [
        entry,
    ]


def test_collection_clear():

    collection = MemoryCollection()

    collection.add(
        create_entry(),
    )

    collection.clear()

    assert len(
        collection,
    ) == 0


def test_collection_len():

    collection = MemoryCollection()

    collection.add(
        create_entry(),
    )

    assert len(
        collection,
    ) == 1


def test_collection_repr():

    collection = MemoryCollection()

    collection.add(
        create_entry(),
    )

    assert (
        repr(
            collection,
        )
        == "MemoryCollection("
        "entries=1)"
    )