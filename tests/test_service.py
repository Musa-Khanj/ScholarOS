from scholaros.services import Service


class DummyService(Service):

    @property
    def name(
        self,
    ) -> str:

        return "Dummy Service"

    @property
    def description(
        self,
    ) -> str:

        return "Dummy service."

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

    def start(
        self,
    ) -> None:

        pass

    def stop(
        self,
    ) -> None:

        pass

    def execute(
        self,
        *args,
        **kwargs,
    ) -> object:

        return None


def create_service() -> DummyService:

    return DummyService()


def test_name_property():

    service = create_service()

    assert service.name == "Dummy Service"


def test_description_property():

    service = create_service()

    assert service.description == "Dummy service."


def test_version_property():

    service = create_service()

    assert service.version == "1.0"


def test_enabled_property():

    service = create_service()

    assert service.enabled is True


def test_execute():

    service = create_service()

    assert service.execute() is None


def test_repr():

    service = create_service()

    assert (
        repr(service)
        == "DummyService(name='Dummy Service', version='1.0', enabled=True)"
    )