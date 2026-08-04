from scholaros.memory.collection import MemoryCollection
from scholaros.memory.entry import MemoryEntry
from scholaros.memory.loader import MemoryLoader
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


def create_loader() -> MemoryLoader:

    registry = MemoryRegistry()

    manager = MemoryManager(
        registry,
    )

    return MemoryLoader(
        manager,
    )


def test_loader_load():

    loader = create_loader()

    collection = create_collection()

    loader.load(
        "Research",
        collection,
    )

    assert (
        loader.manager.get(
            "Research",
        )
        is collection
    )


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

    new_collection = create_collection()

    loader.reload(
        "Research",
        new_collection,
    )

    assert (
        loader.manager.get(
            "Research",
        )
        is new_collection
    )


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
        == "MemoryLoader("
        "collections=1)"
    )