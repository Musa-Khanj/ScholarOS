from scholaros.dependency import DependencyResolver


def create_resolver() -> DependencyResolver:

    return DependencyResolver()


def test_register():

    resolver = create_resolver()

    dependency = object()

    resolver.register(
        "memory",
        dependency,
    )

    assert resolver.contains("memory")


def test_get():

    resolver = create_resolver()

    dependency = object()

    resolver.register(
        "memory",
        dependency,
    )

    assert resolver.get("memory") is dependency


def test_unregister():

    resolver = create_resolver()

    resolver.register(
        "memory",
        object(),
    )

    resolver.unregister("memory")

    assert not resolver.contains("memory")


def test_registered():

    resolver = create_resolver()

    resolver.register(
        "planner",
        object(),
    )

    resolver.register(
        "memory",
        object(),
    )

    assert resolver.registered() == [
        "memory",
        "planner",
    ]


def test_clear():

    resolver = create_resolver()

    resolver.register(
        "runtime",
        object(),
    )

    resolver.clear()

    assert resolver.registered() == []


def test_dependencies_property():

    resolver = create_resolver()

    resolver.register(
        "workflow",
        object(),
    )

    assert "workflow" in resolver.dependencies


def test_repr():

    resolver = create_resolver()

    assert (
        repr(resolver)
        == "DependencyResolver(dependencies=0)"
    )