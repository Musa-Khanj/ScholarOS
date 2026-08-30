"""
ScholarOS
Event & EventBus Tests

Tests for:

- Event
- EventBus
- Subscriber
"""

from __future__ import annotations

import pytest  # type: ignore

from scholaros.events import Event, EventBus
from scholaros.events.subscriber import Subscriber


class DummySubscriber(Subscriber):
    def __init__(self):
        self.called = False

    def handle(self, event: Event):
        self.called = True


# =========================================================
# Event
# =========================================================


def test_event_name():
    """
    Event stores its name.
    """

    event = Event(
        "chat.message",
    )

    assert event.name == "chat.message"


def test_event_default_payload():
    """
    Payload defaults to an empty dict.
    """

    event = Event(
        "event",
    )

    assert event.payload == {}


def test_event_default_metadata():
    """
    Metadata defaults to an empty dict.
    """

    event = Event(
        "event",
    )

    assert event.metadata == {}


def test_event_custom_payload():
    """
    Payload is preserved.
    """

    payload = {
        "text": "Hello",
    }

    event = Event(
        "chat",
        payload=payload,
    )

    assert event.payload == payload


def test_event_custom_metadata():
    """
    Metadata is preserved.
    """

    metadata = {
        "plugin": "core",
    }

    event = Event(
        "chat",
        metadata=metadata,
    )

    assert event.metadata == metadata


def test_event_empty_name_raises():
    """
    Empty names are invalid.
    """

    with pytest.raises(
        ValueError,
    ):
        Event("")


def test_event_whitespace_name_raises():
    """
    Blank names are invalid.
    """

    with pytest.raises(
        ValueError,
    ):
        Event("   ")


# =========================================================
# EventBus
# =========================================================


def test_bus_initially_empty():
    """
    Bus starts empty.
    """

    bus = EventBus()

    assert len(bus) == 0

    assert bus.event_names() == ()


def test_subscribe():
    """
    Listener registration.
    """

    bus = EventBus()

    called = []

    def callback(event):

        called.append(event)

    bus.subscribe(
        "chat",
        callback,
    )

    assert bus.has_subscribers(
        "chat",
    )

    assert len(bus) == 1


def test_duplicate_subscription():
    """
    Duplicate callbacks are ignored.
    """

    bus = EventBus()

    def callback(event):
        pass

    bus.subscribe(
        "chat",
        callback,
    )

    bus.subscribe(
        "chat",
        callback,
    )

    assert len(bus) == 1


def test_unsubscribe():
    """
    Listener removal.
    """

    bus = EventBus()

    def callback(event):
        pass

    bus.subscribe(
        "chat",
        callback,
    )

    assert bus.unsubscribe(
        "chat",
        callback,
    )

    assert len(bus) == 0


def test_unsubscribe_unknown():
    """
    Removing unknown listener returns False.
    """

    bus = EventBus()

    def callback(event):
        pass

    assert bus.unsubscribe(
        "chat",
        callback,
    ) is False


def test_publish():
    """
    Publishing reaches listeners.
    """

    bus = EventBus()

    received = []

    def callback(event):

        received.append(event)

    bus.subscribe(
        "chat",
        callback,
    )

    event = Event(
        "chat",
    )

    bus.publish(
        event,
    )

    assert received == [
        event,
    ]


def test_publish_wrong_type():
    """
    publish() requires Event.
    """

    bus = EventBus()

    with pytest.raises(
        TypeError,
    ):
        bus.publish(
            "chat",
        )


def test_clear():
    """
    clear() removes listeners.
    """

    bus = EventBus()

    def callback(event):
        pass

    bus.subscribe(
        "one",
        callback,
    )

    bus.subscribe(
        "two",
        callback,
    )

    bus.clear()

    assert len(bus) == 0

    assert bus.event_names() == ()


def test_event_names():
    """
    Event names are returned sorted.
    """

    bus = EventBus()

    def callback(event):
        pass

    bus.subscribe(
        "zeta",
        callback,
    )

    bus.subscribe(
        "alpha",
        callback,
    )

    assert bus.event_names() == (
        "alpha",
        "zeta",
    )


def test_listeners():
    """
    listeners() returns tuple.
    """

    bus = EventBus()

    def callback(event):
        pass

    bus.subscribe(
        "chat",
        callback,
    )

    listeners = bus.listeners(
        "chat",
    )

    assert isinstance(
        listeners,
        tuple,
    )

    assert callback in listeners


def test_contains():
    """
    __contains__ delegates correctly.
    """

    bus = EventBus()

    def callback(event):
        pass

    bus.subscribe(
        "chat",
        callback,
    )

    assert "chat" in bus

    assert "missing" not in bus


def test_repr():
    """
    Developer representation.
    """

    bus = EventBus()

    text = repr(
        bus,
    )

    assert text.startswith(
        "EventBus("
    )


def test_subscribe_empty_name():
    """
    Empty event names are rejected.
    """

    bus = EventBus()

    with pytest.raises(
        ValueError,
    ):
        bus.subscribe(
            "",
            lambda event: None,
        )


def test_subscribe_non_callable():
    """
    Callback must be callable.
    """

    bus = EventBus()

    with pytest.raises(
        TypeError,
    ):
        bus.subscribe(
            "chat",
            123,
        )


def test_multiple_callbacks_receive_event():
    """
    All listeners receive events.
    """

    bus = EventBus()

    first = []

    second = []

    def callback_one(event):

        first.append(event)

    def callback_two(event):

        second.append(event)

    bus.subscribe(
        "chat",
        callback_one,
    )

    bus.subscribe(
        "chat",
        callback_two,
    )

    event = Event(
        "chat",
    )

    bus.publish(
        event,
    )

    assert first == [
        event,
    ]

    assert second == [
        event,
    ]


# =========================================================
# Subscriber
# =========================================================


def test_publish_reaches_subscriber():
    """
    Publishing reaches subscribers.
    """

    bus = EventBus()

    sub = DummySubscriber()

    bus.subscribe("hello", sub)

    bus.publish(Event("hello"))

    assert sub.called