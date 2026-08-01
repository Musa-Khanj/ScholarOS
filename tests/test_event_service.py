from scholaros.events import EventBus
from scholaros.events import EventService


def test_event_service_creates_bus():

    service = EventService()

    assert isinstance(
        service.bus,
        EventBus,
    )


def test_event_service_start():

    service = EventService()

    service.start()


def test_event_service_stop():

    service = EventService()

    service.stop()


def test_event_service_bus_available():

    service = EventService()

    assert service.bus is not None