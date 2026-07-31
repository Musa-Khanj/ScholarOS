from scholaros.hooks import Hook


class DummyHook(Hook):
    """
    Concrete implementation used for testing.
    """

    @property
    def name(self) -> str:
        return "Dummy Hook"

    @property
    def description(self) -> str:
        return "Dummy hook."

    @property
    def event(self) -> str:
        return "dummy.event"

    def execute(
        self,
        *args,
        **kwargs,
    ) -> object:
        return None


def create_hook() -> DummyHook:
    """
    Create a fresh DummyHook.
    """

    return DummyHook()


def test_name_property():

    hook = create_hook()

    assert hook.name == "Dummy Hook"


def test_description_property():

    hook = create_hook()

    assert hook.description == "Dummy hook."


def test_event_property():

    hook = create_hook()

    assert hook.event == "dummy.event"


def test_execute():

    hook = create_hook()

    assert hook.execute() is None


def test_repr():

    hook = create_hook()

    assert (
        repr(hook)
        == "DummyHook(name='Dummy Hook', event='dummy.event')"
    )