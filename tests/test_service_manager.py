from scholaros.services import Service
from scholaros.services import ServiceManager


class DummyService(Service):
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

        return "Dummy service"

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


def create_manager() -> ServiceManager:
    """
    Create a fresh ServiceManager.
    """

    return ServiceManager()


def create_service() -> DummyService:
    """
    Create a fresh DummyService.
    """

    return DummyService()


def test_register():

    manager = create_manager()
    service = create_service()

    manager.register(service)

    assert manager.contains("dummy")


def test_get():

    manager = create_manager()
    service = create_service()

    manager.register(service)

    assert manager.get("dummy") is service


def test_unregister():

    manager = create_manager()
    service = create_service()

    manager.register(service)
    manager.unregister("dummy")

    assert not manager.contains("dummy")


def test_registered():

    manager = create_manager()

    manager.register(create_service())

    assert manager.registered() == ["dummy"]


def test_clear():

    manager = create_manager()

    manager.register(create_service())
    manager.clear()

    assert manager.registered() == []


def test_services_property():

    manager = create_manager()

    manager.register(create_service())

    assert "dummy" in manager.services


def test_repr():

    manager = create_manager()

    assert repr(manager) == "ServiceManager(services=0)"