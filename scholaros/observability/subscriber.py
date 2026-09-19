"""
ScholarOS Observability - Telemetry Event Subscriber.

Subscribes to EventBus events across RAG, retrieval, and service lifecycles
to automatically feed metrics into TelemetryCollector and trace registries.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.observability.telemetry import TelemetryCollector

if TYPE_CHECKING:
    from scholaros.events.bus import EventBus


class TelemetryEventSubscriber:
    """
    Listens to application events and converts them into operational telemetry metrics.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        telemetry: TelemetryCollector | None = None,
    ) -> None:
        self.event_bus = event_bus
        self.telemetry = telemetry or TelemetryCollector.get_default()
        self._subscribed = False

    def handle_event(self, event: Any) -> None:
        """Process an incoming event and record relevant telemetry."""
        # Handle Event object or typed RAG event instances
        event_name = getattr(event, "name", type(event).__name__).lower()
        payload: dict[str, Any] = getattr(event, "payload", {})

        # Extract event attributes whether dataclass or Event dictionary payload
        latency_ms = getattr(event, "latency_ms", payload.get("latency_ms", 0.0))
        prompt_tokens = getattr(event, "prompt_tokens", payload.get("prompt_tokens", 0))
        completion_tokens = getattr(event, "completion_tokens", payload.get("completion_tokens", 0))

        if "ragcompleted" in event_name or "rag.completed" in event_name:
            self.telemetry.record_query(
                latency_ms=float(latency_ms),
                success=True,
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
            )
        elif "ragfailed" in event_name or "rag.failed" in event_name:
            self.telemetry.record_query(
                latency_ms=float(latency_ms),
                success=False,
            )
        elif "ragfallback" in event_name or "rag.fallback" in event_name:
            self.telemetry.record_query(
                latency_ms=float(latency_ms),
                success=True,
                fallback=True,
            )

    def subscribe(self, event_bus: EventBus | None = None) -> None:
        """Subscribe to the EventBus."""
        bus = event_bus or self.event_bus
        if bus is None or self._subscribed:
            return

        self.event_bus = bus
        self.PATTERNS = ["rag.*", "RAG*", "service.*", "Service*"]
        for p in self.PATTERNS:
            try:
                bus.subscribe(p, self.handle_event)
            except Exception:
                pass
        self._subscribed = True

    def unsubscribe(self) -> None:
        """Unsubscribe from the EventBus."""
        if self.event_bus is not None and self._subscribed:
            for p in getattr(self, "PATTERNS", ["rag.*", "RAG*", "service.*", "Service*"]):
                try:
                    self.event_bus.unsubscribe(p, self.handle_event)
                except Exception:
                    pass
            self._subscribed = False


__all__ = [
    "TelemetryEventSubscriber",
]
