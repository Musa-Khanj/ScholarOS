"""
ScholarOS Event Subsystem.

Public API for ScholarOS event-driven architecture, event routing,
subscription, dispatching, filtering, priorities, and middleware pipeline.
"""

from __future__ import annotations

from scholaros.events.bus import EventBus
from scholaros.events.context import EventContext
from scholaros.events.dispatcher import EventDispatcher
from scholaros.events.event import Event
from scholaros.events.exceptions import (
    EventCancelledError,
    EventDispatchError,
    EventError,
    HandlerExecutionError,
    MiddlewareError,
    SubscriptionError,
)
from scholaros.events.middleware import (
    EventMiddleware,
    MiddlewarePipeline,
    NextAsync,
    NextSync,
)
from scholaros.events.priority import (
    CRITICAL,
    HIGH,
    LOW,
    MONITOR,
    NORMAL,
    EventPriority,
)
from scholaros.events.publisher import Publisher
from scholaros.events.registry import EventRegistry, Subscription
from scholaros.events.service import EventService
from scholaros.events.subscriber import AsyncSubscriber, Subscriber
from scholaros.events.types import (
    AsyncEventHandler,
    AsyncEventHandlerProtocol,
    EventFilter,
    EventHandler,
    EventHandlerProtocol,
    SyncEventHandler,
)

__all__ = [
    # Core
    "Event",
    "EventBus",
    "EventContext",
    "EventDispatcher",
    "EventRegistry",
    "Publisher",
    "Subscription",
    # Subscribers
    "AsyncSubscriber",
    "Subscriber",
    # Service
    "EventService",
    # Middleware
    "EventMiddleware",
    "MiddlewarePipeline",
    "NextAsync",
    "NextSync",
    # Priority
    "CRITICAL",
    "EventPriority",
    "HIGH",
    "LOW",
    "MONITOR",
    "NORMAL",
    # Exceptions
    "EventCancelledError",
    "EventDispatchError",
    "EventError",
    "HandlerExecutionError",
    "MiddlewareError",
    "SubscriptionError",
    # Types
    "AsyncEventHandler",
    "AsyncEventHandlerProtocol",
    "EventFilter",
    "EventHandler",
    "EventHandlerProtocol",
    "SyncEventHandler",
]