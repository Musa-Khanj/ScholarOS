from scholaros.memory.collection import MemoryCollection
from scholaros.memory.entry import MemoryEntry
from scholaros.memory.registry import MemoryRegistry


def create_collection() -> MemoryCollection:

    collection = MemoryCollection()

    collection.add(
        MemoryEntry(
            entry_id="memory-001",
            content="The user prefers IEEE citations.",
            metadata={
                "source": "conversation",
            },
        ),
    )

    return collection


def test_registry_add():

    registry = MemoryRegistry()

    collection = create_collection()

    registry.add(
        "Research",
        collection,
    )

    assert registry.get(
        "Research",
    ) is collection


def test_registry_get():

    registry = MemoryRegistry()

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

    registry = MemoryRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    assert registry.contains(
        "Research",
    )


def test_registry_remove():

    registry = MemoryRegistry()

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

    registry = MemoryRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    assert registry.names() == [
        "Research",
    ]


def test_registry_values():

    registry = MemoryRegistry()

    collection = create_collection()

    registry.add(
        "Research",
        collection,
    )

    assert registry.values() == [
        collection,
    ]


def test_registry_items():

    registry = MemoryRegistry()

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

    registry = MemoryRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    registry.clear()

    assert len(
        registry,
    ) == 0


def test_registry_repr():

    registry = MemoryRegistry()

    registry.add(
        "Research",
        create_collection(),
    )

    assert (
        repr(
            registry,
        )
        == "MemoryRegistry("
        "collections=1)"
    )