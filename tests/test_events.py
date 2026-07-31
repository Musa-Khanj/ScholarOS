from scholaros.events import Event
from scholaros.events import EventBus
from scholaros.events.subscriber import Subscriber


class DummySubscriber(Subscriber):

    def __init__(self):
        self.called = False

    def handle(self, event: Event):
        self.called = True


def test_publish():

    bus = EventBus()

    sub = DummySubscriber()

    bus.subscribe("hello", sub)

    bus.publish(Event("hello"))

    assert sub.called