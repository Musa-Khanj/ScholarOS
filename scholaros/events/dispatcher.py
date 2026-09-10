"""
ScholarOS Event Dispatcher.

Coordinates invoking event handlers synchronously and asynchronously,
respecting cancellation, handler signatures, and error handling policies.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import TYPE_CHECKING, Any

from scholaros.events.context import EventContext
from scholaros.events.exceptions import (
    EventCancelledError,
    EventDispatchError,
    HandlerExecutionError,
)

if TYPE_CHECKING:
    from scholaros.events.event import Event
    from scholaros.events.registry import Subscription


class EventDispatcher:
    """
    Dispatches events to registered subscriptions.
    """

    def __init__(self, stop_on_error: bool = False) -> None:
        self.stop_on_error = stop_on_error

    def dispatch(
        self,
        event: Event,
        subscriptions: list[Subscription],
        context: EventContext,
    ) -> list[Any]:
        """
        Dispatch the event synchronously across all matched subscriptions.
        Returns the collected results of handler invocations.
        """
        results: list[Any] = []
        errors: list[Exception] = []

        for sub in subscriptions:
            if context.is_cancelled:
                break

            try:
                result = self._invoke_sync(sub.handler, event, context)
                results.append(result)
            except Exception as exc:
                handler_name = getattr(sub.handler, "__name__", str(sub.handler))
                err = HandlerExecutionError(handler_name, exc)
                errors.append(err)
                if self.stop_on_error:
                    raise EventDispatchError(
                        f"Dispatch aborted on handler {handler_name}",
                        errors=errors,
                    ) from exc

        if errors and self.stop_on_error:
            raise EventDispatchError("One or more handlers failed during dispatch", errors=errors)

        return results

    async def dispatch_async(
        self,
        event: Event,
        subscriptions: list[Subscription],
        context: EventContext,
    ) -> list[Any]:
        """
        Dispatch the event asynchronously across matched subscriptions.
        Supports both sync and async handlers in the same pipeline.
        """
        results: list[Any] = []
        errors: list[Exception] = []

        for sub in subscriptions:
            if context.is_cancelled:
                break

            try:
                result = await self._invoke_async(sub.handler, event, context)
                results.append(result)
            except Exception as exc:
                handler_name = getattr(sub.handler, "__name__", str(sub.handler))
                err = HandlerExecutionError(handler_name, exc)
                errors.append(err)
                if self.stop_on_error:
                    raise EventDispatchError(
                        f"Async dispatch aborted on handler {handler_name}",
                        errors=errors,
                    ) from exc

        if errors and self.stop_on_error:
            raise EventDispatchError("One or more handlers failed during async dispatch", errors=errors)

        return results

    def _invoke_sync(
        self,
        handler: Any,
        event: Event,
        context: EventContext,
    ) -> Any:
        handler_callable = handler if callable(handler) else getattr(handler, "handle")
        handler_name = getattr(handler_callable, "__qualname__", getattr(handler, "__class__", type(handler)).__name__)
        context.record_handler(handler_name)

        # Check parameter count
        sig = inspect.signature(handler_callable)
        params = list(sig.parameters.values())

        if len(params) >= 2:
            res = handler_callable(event, context)
        else:
            res = handler_callable(event)

        # If it returned a coroutine in sync dispatch, run it in new loop or through asyncio if possible
        if inspect.iscoroutine(res):
            try:
                loop = asyncio.get_running_loop()
                # If event loop is already running, schedule background task
                loop.create_task(res)
                return None
            except RuntimeError:
                return asyncio.run(res)

        return res

    async def _invoke_async(
        self,
        handler: Any,
        event: Event,
        context: EventContext,
    ) -> Any:
        if hasattr(handler, "handle_async") and callable(handler.handle_async):
            handler_callable = handler.handle_async
        elif callable(handler):
            handler_callable = handler
        else:
            handler_callable = getattr(handler, "handle")

        handler_name = getattr(handler_callable, "__qualname__", getattr(handler, "__class__", type(handler)).__name__)
        context.record_handler(handler_name)

        sig = inspect.signature(handler_callable)
        params = list(sig.parameters.values())

        if len(params) >= 2:
            res = handler_callable(event, context)
        else:
            res = handler_callable(event)

        if inspect.isawaitable(res):
            return await res
        return res


__all__ = [
    "EventDispatcher",
]
