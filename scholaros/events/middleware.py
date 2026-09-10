"""
ScholarOS Event Middleware.

Defines the middleware interface and pipeline for intercepting, modifying,
logging, or filtering events before and after dispatch.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
import inspect
from typing import Any

from scholaros.events.context import EventContext
from scholaros.events.event import Event

# Next function: Callable[[Event, EventContext], Any]
NextSync = Callable[[Event, EventContext], Any]
NextAsync = Callable[[Event, EventContext], Awaitable[Any]]


class EventMiddleware(ABC):
    """
    Abstract base class for event middleware.
    Interception point for events traversing the event bus.
    """

    @abstractmethod
    def process(
        self,
        event: Event,
        context: EventContext,
        next_handler: NextSync,
    ) -> Any:
        """
        Process event synchronously.

        Implementations must invoke next_handler(event, context) to proceed,
        unless they intentionally halt processing or modify the event.
        """
        ...

    async def process_async(
        self,
        event: Event,
        context: EventContext,
        next_handler: NextAsync,
    ) -> Any:
        """
        Process event asynchronously.
        Defaults to delegating to process() if not overridden.
        """
        # Default fallback calls synchronous process if no async specialization
        res = self.process(event, context, lambda e, c: next_handler(e, c))
        if inspect.isawaitable(res):
            return await res
        return res


class MiddlewarePipeline:
    """
    Executes a chain of EventMiddleware layers wrapping a terminal dispatch function.
    """

    def __init__(self) -> None:
        self._middlewares: list[EventMiddleware] = []

    def use(self, middleware: EventMiddleware) -> None:
        """Add a middleware to the end of the pipeline."""
        if not isinstance(middleware, EventMiddleware):
            raise TypeError("Middleware must inherit from EventMiddleware")
        self._middlewares.append(middleware)

    def remove(self, middleware: EventMiddleware) -> bool:
        """Remove a middleware from the pipeline."""
        try:
            self._middlewares.remove(middleware)
            return True
        except ValueError:
            return False

    def clear(self) -> None:
        """Clear all registered middlewares."""
        self._middlewares.clear()

    def execute(
        self,
        event: Event,
        context: EventContext,
        terminal: NextSync,
    ) -> Any:
        """
        Execute the synchronous middleware pipeline wrapping terminal dispatch.
        """
        def build_chain(index: int) -> NextSync:
            if index >= len(self._middlewares):
                return terminal

            current_mw = self._middlewares[index]
            next_step = build_chain(index + 1)

            def chain_step(evt: Event, ctx: EventContext) -> Any:
                if ctx.is_cancelled:
                    return None
                return current_mw.process(evt, ctx, next_step)

            return chain_step

        pipeline = build_chain(0)
        return pipeline(event, context)

    async def execute_async(
        self,
        event: Event,
        context: EventContext,
        terminal: NextAsync,
    ) -> Any:
        """
        Execute the asynchronous middleware pipeline wrapping terminal dispatch.
        """
        def build_async_chain(index: int) -> NextAsync:
            if index >= len(self._middlewares):
                return terminal

            current_mw = self._middlewares[index]
            next_step = build_async_chain(index + 1)

            async def async_chain_step(evt: Event, ctx: EventContext) -> Any:
                if ctx.is_cancelled:
                    return None
                return await current_mw.process_async(evt, ctx, next_step)

            return async_chain_step

        pipeline = build_async_chain(0)
        return await pipeline(event, context)

    def __len__(self) -> int:
        return len(self._middlewares)


__all__ = [
    "EventMiddleware",
    "MiddlewarePipeline",
    "NextAsync",
    "NextSync",
]
