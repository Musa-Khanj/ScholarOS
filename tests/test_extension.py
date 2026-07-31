from scholaros.extensions import Extension


class DummyExtension(Extension):

    @property
    def name(
        self,
    ) -> str:

        return "Dummy Extension"

    @property
    def description(
        self,
    ) -> str:

        return "Dummy extension."

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


def create_extension() -> DummyExtension:

    return DummyExtension()


def test_name_property():

    extension = create_extension()

    assert extension.name == "Dummy Extension"


def test_description_property():

    extension = create_extension()

    assert extension.description == "Dummy extension."


def test_version_property():

    extension = create_extension()

    assert extension.version == "1.0"


def test_enabled_property():

    extension = create_extension()

    assert extension.enabled is True


def test_execute():

    extension = create_extension()

    assert extension.execute() is None


def test_repr():

    extension = create_extension()

    assert (
        repr(extension)
        == "DummyExtension(name='Dummy Extension', version='1.0', enabled=True)"
    )