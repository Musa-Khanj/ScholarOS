from scholaros.extensions import Extension
from scholaros.extensions import ExtensionManager


class DummyExtension(Extension):
    """
    Concrete implementation used for testing.
    """

    @property
    def name(
        self,
    ) -> str:

        return "dummy"

    @property
    def description(
        self,
    ) -> str:

        return "Dummy extension"

    @property
    def version(
        self,
    ) -> str:

        return "1.0"

    @property
    def enabled(
        self,
    ) -> bool:

        return True

    def enable(
        self,
    ) -> None:

        pass

    def disable(
        self,
    ) -> None:

        pass

    def execute(
        self,
        *args,
        **kwargs,
    ) -> object:

        return None


def create_manager() -> ExtensionManager:
    """
    Create a fresh ExtensionManager.
    """

    return ExtensionManager()


def create_extension() -> DummyExtension:
    """
    Create a fresh DummyExtension.
    """

    return DummyExtension()


def test_register():

    manager = create_manager()
    extension = create_extension()

    manager.register(extension)

    assert manager.contains("dummy")


def test_get():

    manager = create_manager()
    extension = create_extension()

    manager.register(extension)

    assert manager.get("dummy") is extension


def test_unregister():

    manager = create_manager()
    extension = create_extension()

    manager.register(extension)
    manager.unregister("dummy")

    assert not manager.contains("dummy")


def test_registered():

    manager = create_manager()

    manager.register(create_extension())

    assert manager.registered() == ["dummy"]


def test_clear():

    manager = create_manager()

    manager.register(create_extension())
    manager.clear()

    assert manager.registered() == []


def test_extensions_property():

    manager = create_manager()

    manager.register(create_extension())

    assert "dummy" in manager.extensions


def test_repr():

    manager = create_manager()

    assert repr(manager) == "ExtensionManager(extensions=0)"
