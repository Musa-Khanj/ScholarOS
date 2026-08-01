from scholaros.events import Event
from scholaros.events import EventBus
from scholaros.events.publisher import Publisher
from scholaros.events.service import EventService
from scholaros.events.subscriber import Subscriber


class DummySubscriber(Subscriber):

    def __init__(self) -> None:

        self.events: list[Event] = []

    def handle(
        self,
        event: Event,
    ) -> None:

        self.events.append(event)


def create_bus() -> EventBus:

    return EventBus()


def test_subscribe():

    bus = create_bus()
    subscriber = DummySubscriber()

    bus.subscribe(
        "research.completed",
        subscriber,
    )

    event = Event(
        name="research.completed",
    )

    bus.publish(event)

    assert subscriber.events == [
        event,
    ]


def test_unsubscribe():

    bus = create_bus()
    subscriber = DummySubscriber()

    bus.subscribe(
        "research.completed",
        subscriber,
    )

    bus.unsubscribe(
        "research.completed",
        subscriber,
    )

    bus.publish(
        Event(
            name="research.completed",
        )
    )

    assert subscriber.events == []


def test_multiple_subscribers():

    bus = create_bus()

    first = DummySubscriber()
    second = DummySubscriber()

    event = Event(
        name="runtime.started",
    )

    bus.subscribe(
        "runtime.started",
        first,
    )

    bus.subscribe(
        "runtime.started",
        second,
    )

    bus.publish(event)

    assert first.events == [
        event,
    ]

    assert second.events == [
        event,
    ]


def test_event_payload():

    event = Event(
        name="planner.finished",
        payload={
            "steps": 5,
        },
    )

    assert event.payload[
        "steps"
    ] == 5


def test_publisher():

    bus = create_bus()

    subscriber = DummySubscriber()

    publisher = Publisher(bus)

    bus.subscribe(
        "workflow.started",
        subscriber,
    )

    event = Event(
        name="workflow.started",
    )

    publisher.publish(
        event,
    )

    assert subscriber.events == [
        event,
    ]


def test_event_service():

    service = EventService()

    assert isinstance(
        service.bus,
        EventBus,
    )

def test_event_metadata():

    event = Event(
        name="runtime.started",
    )

    assert event.id
    assert event.timestamp is not None