from scholaros.plugins.base import Plugin
from scholaros.plugins.manifest import PluginManifest
from scholaros.plugins.registry import PluginRegistry


class DummyPlugin(Plugin):

    def __init__(self) -> None:

        self.manifest = PluginManifest(
            name="dummy",
            version="1.0",
            author="ScholarOS",
            description="Dummy plugin",
            scholaros="1.0",
            license="MIT",
        )

    def install(self) -> None:
        pass

    def uninstall(self) -> None:
        pass

    def enable(self) -> None:
        pass

    def disable(self) -> None:
        pass


class AlphaPlugin(Plugin):

    def __init__(self) -> None:

        self.manifest = PluginManifest(
            name="alpha",
            version="1.0",
            author="ScholarOS",
            description="Alpha plugin",
            scholaros="1.0",
            license="MIT",
        )

    def install(self) -> None:
        pass

    def uninstall(self) -> None:
        pass

    def enable(self) -> None:
        pass

    def disable(self) -> None:
        pass


class BetaPlugin(Plugin):

    def __init__(self) -> None:

        self.manifest = PluginManifest(
            name="beta",
            version="1.0",
            author="ScholarOS",
            description="Beta plugin",
            scholaros="1.0",
            license="MIT",
        )

    def install(self) -> None:
        pass

    def uninstall(self) -> None:
        pass

    def enable(self) -> None:
        pass

    def disable(self) -> None:
        pass


def create_registry() -> PluginRegistry:

    return PluginRegistry()


def test_registry_starts_empty():

    registry = create_registry()

    assert registry.names() == []
    assert registry.values() == []
    assert registry.items() == []
    assert not registry.contains("dummy")


def test_add_plugin():

    registry = create_registry()
    plugin = DummyPlugin()

    registry.add(plugin)

    assert registry.contains("dummy")
    assert registry.get("dummy") is plugin


def test_remove_plugin():

    registry = create_registry()

    registry.add(DummyPlugin())
    registry.remove("dummy")

    assert not registry.contains("dummy")


def test_clear_registry():

    registry = create_registry()

    registry.add(DummyPlugin())
    registry.add(AlphaPlugin())

    registry.clear()

    assert registry.names() == []


def test_names_are_sorted():

    registry = create_registry()

    registry.add(DummyPlugin())
    registry.add(BetaPlugin())
    registry.add(AlphaPlugin())

    assert registry.names() == [
        "alpha",
        "beta",
        "dummy",
    ]


def test_values():

    registry = create_registry()

    alpha = AlphaPlugin()
    beta = BetaPlugin()

    registry.add(alpha)
    registry.add(beta)

    values = registry.values()

    assert alpha in values
    assert beta in values
    assert len(values) == 2


def test_items():

    registry = create_registry()

    plugin = DummyPlugin()

    registry.add(plugin)

    assert registry.items() == [
        ("dummy", plugin),
    ]


def test_contains():

    registry = create_registry()

    registry.add(DummyPlugin())

    assert registry.contains("dummy")
    assert not registry.contains("missing")


def test_repr():

    registry = create_registry()

    assert repr(registry) == "PluginRegistry(plugins=0)"

    registry.add(DummyPlugin())

    assert repr(registry) == "PluginRegistry(plugins=1)"