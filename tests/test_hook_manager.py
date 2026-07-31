from scholaros.hooks import Hook
from scholaros.hooks import HookManager


class DummyHook(Hook):
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

        return "Dummy hook"

    @property
    def event(
        self,
    ) -> str:

        return "dummy.event"

    def execute(
        self,
        *args,
        **kwargs,
    ) -> object:

        return None


def create_manager() -> HookManager:
    """
    Create a fresh HookManager.
    """

    return HookManager()


def create_hook() -> DummyHook:
    """
    Create a fresh DummyHook.
    """

    return DummyHook()


def test_register():

    manager = create_manager()
    hook = create_hook()

    manager.register(hook)

    assert manager.contains("dummy")


def test_get():

    manager = create_manager()
    hook = create_hook()

    manager.register(hook)

    assert manager.get("dummy") is hook


def test_unregister():

    manager = create_manager()
    hook = create_hook()

    manager.register(hook)
    manager.unregister("dummy")

    assert not manager.contains("dummy")


def test_registered():

    manager = create_manager()

    manager.register(create_hook())

    assert manager.registered() == ["dummy"]


def test_clear():

    manager = create_manager()

    manager.register(create_hook())
    manager.clear()

    assert manager.registered() == []


def test_hooks_property():

    manager = create_manager()

    manager.register(create_hook())

    assert "dummy" in manager.hooks


def test_repr():

    manager = create_manager()

    assert repr(manager) == "HookManager(hooks=0)"