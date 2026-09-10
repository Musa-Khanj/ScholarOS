"""
ScholarOS Event Bus.

Central publish-subscribe event routing engine with support for:
- Synchronous and asynchronous publication and dispatch
- Priority-ordered handler invocation
- Predicate filtering and pattern matching
- Interceptor middleware pipeline
- Propagation cancellation and execution context
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from scholaros.events.context import EventContext
from scholaros.events.dispatcher import EventDispatcher
from scholaros.events.event import Event
from scholaros.events.middleware import EventMiddleware, MiddlewarePipeline
from scholaros.events.priority import EventPriority
from scholaros.events.registry import EventRegistry, Subscription
from scholaros.events.types import EventFilter, EventHandler


class EventBus:
    """
    Publish-subscribe event dispatcher and routing engine.
    """

    def __init__(self, stop_on_error: bool = False) -> None:
        """Initialize the event bus."""
        self.registry = EventRegistry()
        self.dispatcher = EventDispatcher(stop_on_error=stop_on_error)
        self.middlewares = MiddlewarePipeline()

    # ---------------------------------------------------------
    # Middleware
    # ---------------------------------------------------------

    def use(self, middleware: EventMiddleware) -> EventBus:
        """Add middleware to the dispatch pipeline. Returns self for chaining."""
        self.middlewares.use(middleware)
        return self

    # ---------------------------------------------------------
    # Subscription
    # ---------------------------------------------------------

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler,
        priority: int = EventPriority.NORMAL,
        filters: list[EventFilter] | None = None,
        once: bool = False,
    ) -> Subscription:
        """
        Subscribe a handler to an event name or pattern.
        """
        if not isinstance(event_name, str):
            raise TypeError("Event name must be a string.")

        if not event_name.strip():
            raise ValueError("Event name cannot be empty.")

        if not (
            callable(handler)
            or hasattr(handler, "handle")
            or hasattr(handler, "handle_async")
        ):
            raise TypeError(
                "Handler must be callable or implement handle() / handle_async()."
            )

        # If handler has priority or filters defined on instance, use as default
        handler_priority = getattr(handler, "priority", priority)
        handler_filters = list(filters or [])
        if hasattr(handler, "filters") and isinstance(handler.filters, list):
            for f in handler.filters:
                if f not in handler_filters:
                    handler_filters.append(f)

        return self.registry.register(
            event_pattern=event_name,
            handler=handler,
            priority=handler_priority,
            filters=handler_filters,
            once=once,
        )

    def unsubscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> bool:
        """
        Remove a subscribed handler.

        Returns True if removed.
        """
        return self.registry.unregister(event_name, handler)

    # ---------------------------------------------------------
    # Publishing & Dispatching
    # ---------------------------------------------------------

    def publish(
        self,
        event: Event,
        context: EventContext | None = None,
    ) -> list[Any]:
        """
        Publish an event synchronously through middleware and matched handlers.
        """
        if not isinstance(event, Event):
            raise TypeError("Expected Event instance.")

        ctx = context or EventContext()
        subscriptions = self.registry.get_subscriptions_for(event)

        # One-shot subscription cleanup
        for sub in subscriptions:
            if sub.once:
                self.registry.remove_subscription(sub)

        def terminal_dispatch(evt: Event, c: EventContext) -> list[Any]:
            return self.dispatcher.dispatch(evt, subscriptions, c)

        return self.middlewares.execute(event, ctx, terminal_dispatch)

    async def publish_async(
        self,
        event: Event,
        context: EventContext | None = None,
    ) -> list[Any]:
        """
        Publish an event asynchronously through middleware and matched handlers.
        """
        if not isinstance(event, Event):
            raise TypeError("Expected Event instance.")

        ctx = context or EventContext()
        subscriptions = self.registry.get_subscriptions_for(event)

        for sub in subscriptions:
            if sub.once:
                self.registry.remove_subscription(sub)

        async def terminal_async_dispatch(evt: Event, c: EventContext) -> list[Any]:
            return await self.dispatcher.dispatch_async(evt, subscriptions, c)

        return await self.middlewares.execute_async(event, ctx, terminal_async_dispatch)

    def dispatch(
        self,
        event: Event,
        context: EventContext | None = None,
    ) -> list[Any]:
        """Alias for publish()."""
        return self.publish(event, context=context)

    async def dispatch_async(
        self,
        event: Event,
        context: EventContext | None = None,
    ) -> list[Any]:
        """Alias for publish_async()."""
        return await self.publish_async(event, context=context)

    # ---------------------------------------------------------
    # Introspection
    # ---------------------------------------------------------

    def listeners(
        self,
        event_name: str,
    ) -> tuple[EventHandler, ...]:
        """Return listeners registered for an event name."""
        return self.registry.listeners_for(event_name)

    def event_names(self) -> tuple[str, ...]:
        """Return registered event names."""
        return self.registry.event_names()

    def has_subscribers(
        self,
        event_name: str,
    ) -> bool:
        """Return True if listeners exist for this event name."""
        return self.registry.has_subscribers(event_name)

    # ---------------------------------------------------------
    # Maintenance
    # ---------------------------------------------------------

    def clear(self) -> None:
        """Remove every subscription."""
        self.registry.clear()

    # ---------------------------------------------------------
    # Magic Methods
    # ---------------------------------------------------------

    def __contains__(
        self,
        event_name: object,
    ) -> bool:
        return event_name in self.registry

    def __len__(self) -> int:
        """Number of registered event names."""
        return len(self.event_names())


    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"events={len(self.event_names())}, "
            f"subscriptions={len(self.registry)}"
            f")"
        )


__all__ = [
    "EventBus",
    "EventHandler",
]