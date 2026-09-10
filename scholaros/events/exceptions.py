"""
ScholarOS Event System Exceptions.

Exception hierarchy for event publication, dispatching, subscription,
and middleware execution.
"""

from __future__ import annotations


class EventError(Exception):
    """Base class for all event system exceptions."""


class EventDispatchError(EventError):
    """Raised when an error occurs during event dispatching to handlers."""

    def __init__(self, message: str, errors: list[Exception] | None = None) -> None:
        super().__init__(message)
        self.errors: list[Exception] = errors or []


class SubscriptionError(EventError):
    """Raised when a subscription registration or unregistration is invalid."""


class HandlerExecutionError(EventError):
    """Raised when a specific event handler raises an unhandled exception."""

    def __init__(self, handler_name: str, original_error: Exception) -> None:
        super().__init__(f"Handler '{handler_name}' failed: {original_error}")
        self.handler_name = handler_name
        self.original_error = original_error


class MiddlewareError(EventError):
    """Raised when an error occurs during middleware pipeline execution."""


class EventCancelledError(EventError):
    """Raised or used when an event propagation is cancelled in context."""


__all__ = [
    "EventCancelledError",
    "EventDispatchError",
    "EventError",
    "HandlerExecutionError",
    "MiddlewareError",
    "SubscriptionError",
]
