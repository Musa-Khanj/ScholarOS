from scholaros.registry import RegistryManager
from scholaros.registry import ServiceRegistry


def create_manager() -> RegistryManager:

    return RegistryManager()


def create_registry() -> ServiceRegistry:

    return ServiceRegistry()


def test_register():

    manager = create_manager()
    registry = create_registry()

    manager.register(
        "default",
        registry,
    )

    assert manager.contains("default")


def test_get():

    manager = create_manager()
    registry = create_registry()

    manager.register(
        "default",
        registry,
    )

    assert manager.get("default") is registry


def test_unregister():

    manager = create_manager()
    registry = create_registry()

    manager.register(
        "default",
        registry,
    )

    manager.unregister("default")

    assert not manager.contains("default")


def test_registered():

    manager = create_manager()

    manager.register(
        "default",
        create_registry(),
    )

    assert manager.registered() == [
        "default",
    ]


def test_clear():

    manager = create_manager()

    manager.register(
        "default",
        create_registry(),
    )

    manager.clear()

    assert manager.registered() == []


def test_registries_property():

    manager = create_manager()

    manager.register(
        "default",
        create_registry(),
    )

    assert "default" in manager.registries


def test_repr():

    manager = create_manager()

    assert (
        repr(manager)
        == "RegistryManager(registries=0)"
    )