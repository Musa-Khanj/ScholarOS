from scholaros.lifecycle import LifecycleManager
from scholaros.lifecycle import LifecycleState


def create_manager() -> LifecycleManager:

    return LifecycleManager()


def test_register():

    manager = create_manager()

    component = object()

    manager.register(
        "runtime",
        component,
    )

    assert manager.contains("runtime")


def test_get():

    manager = create_manager()

    component = object()

    manager.register(
        "runtime",
        component,
    )

    assert manager.get("runtime") is component


def test_unregister():

    manager = create_manager()

    manager.register(
        "runtime",
        object(),
    )

    manager.unregister("runtime")

    assert not manager.contains("runtime")


def test_registered():

    manager = create_manager()

    manager.register(
        "planner",
        object(),
    )

    manager.register(
        "runtime",
        object(),
    )

    assert manager.registered() == [
        "planner",
        "runtime",
    ]


def test_clear():

    manager = create_manager()

    manager.register(
        "runtime",
        object(),
    )

    manager.clear()

    assert manager.registered() == []


def test_components_property():

    manager = create_manager()

    manager.register(
        "runtime",
        object(),
    )

    assert "runtime" in manager.components


def test_repr():

    manager = create_manager()

    assert (
        repr(manager)
        == "LifecycleManager(components=0)"
    )


def test_lifecycle_states():

    assert LifecycleState.CREATED == "created"
    assert LifecycleState.INITIALIZED == "initialized"
    assert LifecycleState.STARTING == "starting"
    assert LifecycleState.RUNNING == "running"
    assert LifecycleState.STOPPING == "stopping"
    assert LifecycleState.STOPPED == "stopped"