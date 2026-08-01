from scholaros.dependency import DependencyContainer


def create_container() -> DependencyContainer:

    return DependencyContainer()


def test_register():

    container = create_container()

    dependency = object()

    container.register(
        "memory",
        dependency,
    )

    assert container.contains("memory")


def test_resolve():

    container = create_container()

    dependency = object()

    container.register(
        "memory",
        dependency,
    )

    assert (
        container.resolve("memory")
        is dependency
    )


def test_unregister():

    container = create_container()

    container.register(
        "memory",
        object(),
    )

    container.unregister("memory")

    assert not container.contains("memory")


def test_clear():

    container = create_container()

    container.register(
        "runtime",
        object(),
    )

    container.clear()

    assert (
        container.resolver.registered()
        == []
    )


def test_resolver_property():

    container = create_container()

    assert (
        container.resolver
        is not None
    )


def test_repr():

    container = create_container()

    assert (
        repr(container)
        == "DependencyContainer(dependencies=0)"
    )