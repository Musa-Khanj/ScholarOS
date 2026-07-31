from scholaros.memory import Memory


def create_memory() -> Memory:

    return Memory()


def test_storage_property():

    memory = create_memory()

    assert isinstance(
        memory.storage,
        dict,
    )


def test_set_and_get():

    memory = create_memory()

    memory.set(
        "topic",
        "Artificial Intelligence",
    )

    assert (
        memory.get("topic")
        == "Artificial Intelligence"
    )


def test_get_default():

    memory = create_memory()

    assert (
        memory.get(
            "missing",
            "default",
        )
        == "default"
    )


def test_remove():

    memory = create_memory()

    memory.set(
        "key",
        "value",
    )

    memory.remove(
        "key",
    )

    assert (
        memory.get("key")
        is None
    )


def test_clear():

    memory = create_memory()

    memory.set(
        "a",
        1,
    )

    memory.set(
        "b",
        2,
    )

    memory.clear()

    assert memory.storage == {}


def test_repr():

    memory = create_memory()

    memory.set(
        "topic",
        "AI",
    )

    assert (
        repr(memory)
        == "Memory(size=1)"
    )