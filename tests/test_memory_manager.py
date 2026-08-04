from scholaros.memory.collection import MemoryCollection
from scholaros.memory.entry import MemoryEntry
from scholaros.memory.manager import MemoryManager
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


def create_manager() -> MemoryManager:

    registry = MemoryRegistry()

    return MemoryManager(
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

    assert manager.get(
        "Research",
    ) is collection


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
        == "MemoryManager("
        "collections=1)"
    )