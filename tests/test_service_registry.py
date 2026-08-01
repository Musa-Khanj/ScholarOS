from scholaros.registry import ServiceRegistry


def create_registry() -> ServiceRegistry:

    return ServiceRegistry()


def test_register():

    registry = create_registry()

    service = object()

    registry.register(
        "memory",
        service,
    )

    assert registry.contains("memory")


def test_get():

    registry = create_registry()

    service = object()

    registry.register(
        "memory",
        service,
    )

    assert registry.get("memory") is service


def test_unregister():

    registry = create_registry()

    registry.register(
        "memory",
        object(),
    )

    registry.unregister("memory")

    assert not registry.contains("memory")


def test_registered():

    registry = create_registry()

    registry.register(
        "planner",
        object(),
    )

    registry.register(
        "memory",
        object(),
    )

    assert registry.registered() == [
        "memory",
        "planner",
    ]


def test_clear():

    registry = create_registry()

    registry.register(
        "runtime",
        object(),
    )

    registry.clear()

    assert registry.registered() == []


def test_services_property():

    registry = create_registry()

    registry.register(
        "workflow",
        object(),
    )

    assert "workflow" in registry.services


def test_repr():

    registry = create_registry()

    assert (
        repr(registry)
        == "ServiceRegistry(services=0)"
    )