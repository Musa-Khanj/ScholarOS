import pytest
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


def test_event_service_register_container():
    from scholaros.container import Container
    from scholaros.events import Publisher

    container = Container()
    service = EventService.configure_container(container)

    resolved_bus = container.resolve(EventBus)
    resolved_service = container.resolve(EventService)
    resolved_publisher = container.resolve(Publisher)

    assert resolved_bus is service.bus
    assert resolved_service is service
    assert isinstance(resolved_publisher, Publisher)
    assert resolved_publisher.bus is service.bus


def test_event_priority_ordering():
    from scholaros.events import CRITICAL, HIGH, LOW, Event, EventPriority

    bus = EventBus()
    order = []

    bus.subscribe("data.process", lambda e: order.append("normal"), priority=EventPriority.NORMAL)
    bus.subscribe("data.process", lambda e: order.append("low"), priority=LOW)
    bus.subscribe("data.process", lambda e: order.append("high"), priority=HIGH)
    bus.subscribe("data.process", lambda e: order.append("critical"), priority=CRITICAL)

    bus.publish(Event("data.process"))

    assert order == ["critical", "high", "normal", "low"]


def test_event_filtering():
    from scholaros.events import Event

    bus = EventBus()
    received = []

    # Only accept events with importance == "high"
    bus.subscribe(
        "task.created",
        lambda e: received.append(e.payload.get("task")),
        filters=[lambda e: e.payload.get("importance") == "high"],
    )

    bus.publish(Event("task.created", payload={"task": "ignored", "importance": "low"}))
    bus.publish(Event("task.created", payload={"task": "accepted", "importance": "high"}))

    assert received == ["accepted"]


def test_event_context_propagation_stop():
    from scholaros.events import Event, EventContext

    bus = EventBus()
    calls = []

    def first_handler(event: Event, context: EventContext):
        calls.append("first")
        context.stop_propagation(reason="handled")

    def second_handler(event: Event):
        calls.append("second")

    bus.subscribe("action", first_handler, priority=10)
    bus.subscribe("action", second_handler, priority=5)

    ctx = EventContext()
    bus.publish(Event("action"), context=ctx)

    assert calls == ["first"]
    assert ctx.is_cancelled is True
    assert ctx.cancel_reason == "handled"


def test_event_middleware_pipeline():
    from scholaros.events import Event, EventContext, EventMiddleware

    class LoggingMiddleware(EventMiddleware):
        def __init__(self):
            self.log = []

        def process(self, event, context, next_handler):
            self.log.append(f"before:{event.name}")
            res = next_handler(event, context)
            self.log.append(f"after:{event.name}")
            return res

    bus = EventBus()
    mw = LoggingMiddleware()
    bus.use(mw)

    dispatched = []
    bus.subscribe("item.saved", lambda e: dispatched.append(e.name))

    bus.publish(Event("item.saved"))

    assert dispatched == ["item.saved"]
    assert mw.log == ["before:item.saved", "after:item.saved"]


@pytest.mark.anyio
async def test_async_event_dispatch():
    import pytest
    from scholaros.events import AsyncSubscriber, Event

    bus = EventBus()
    records = []

    class MyAsyncSub(AsyncSubscriber):
        async def handle_async(self, event, context=None):
            records.append(f"async:{event.name}")

    bus.subscribe("async.topic", MyAsyncSub())
    await bus.publish_async(Event("async.topic"))

    assert records == ["async:async.topic"]