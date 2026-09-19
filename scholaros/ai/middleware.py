"""
ScholarOS AI Middleware Pipeline.

Provides request/response interceptors for logging, telemetry, caching, and safety guardrails.
"""

from __future__ import annotations

import logging
import re
import time
from abc import ABC
from collections.abc import Callable
from typing import TYPE_CHECKING

from scholaros.ai.exceptions import SafetyViolationError
from scholaros.ai.response import AIResponse

if TYPE_CHECKING:
    from scholaros.ai.cache import ResponseCache
    from scholaros.ai.metrics import AIMetrics
    from scholaros.ai.request import AIRequest

logger = logging.getLogger("scholaros.ai")


class AIMiddleware(ABC):
    """
    Base class for AI request and response middleware.
    """

    def process_request(self, request: AIRequest) -> AIRequest:
        """Inspect or mutate request before provider execution."""
        return request

    def process_response(self, request: AIRequest, response: AIResponse) -> AIResponse:
        """Inspect or mutate response after provider execution."""
        return response


class LoggingMiddleware(AIMiddleware):
    """Logs outgoing requests and incoming responses."""

    def process_request(self, request: AIRequest) -> AIRequest:
        logger.debug("AI Request started: model=%s, messages=%d", request.model, len(request.messages))
        return request

    def process_response(self, request: AIRequest, response: AIResponse) -> AIResponse:
        logger.debug(
            "AI Response received: model=%s, tokens=%d, latency=%.1fms",
            response.model,
            response.total_tokens,
            response.latency_ms,
        )
        return response


class TelemetryMiddleware(AIMiddleware):
    """Records request latencies, token consumption, and failure stats."""

    def __init__(self, metrics: AIMetrics) -> None:
        self.metrics = metrics

    def process_response(self, request: AIRequest, response: AIResponse) -> AIResponse:
        self.metrics.record_request(
            latency_ms=response.latency_ms,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            cost=response.cost,
            success=True,
        )
        return response


class CachingMiddleware(AIMiddleware):
    """Intercepts requests to serve cached responses when available."""

    def __init__(self, cache: ResponseCache) -> None:
        self.cache = cache

    def process_response(self, request: AIRequest, response: AIResponse) -> AIResponse:
        # Cache non-empty responses
        if response.has_content:
            key = self.cache.make_key(request)
            self.cache.set(key, response)
        return response


class SafetyMiddleware(AIMiddleware):
    """Detects basic prompt injection and safety violations."""

    DEFAULT_BLOCKED_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"system\s*override\s*:\s*admin",
    ]

    def __init__(self, blocked_patterns: list[str] | None = None) -> None:
        patterns = blocked_patterns or self.DEFAULT_BLOCKED_PATTERNS
        self._regexes = [re.compile(p, re.IGNORECASE) for p in patterns]

    def process_request(self, request: AIRequest) -> AIRequest:
        content_to_check: list[str] = []
        if request.prompt:
            content_to_check.append(request.prompt)
        for msg in request.messages:
            content_to_check.append(msg.content)

        full_text = " ".join(content_to_check)
        for pattern in self._regexes:
            if pattern.search(full_text):
                raise SafetyViolationError("Safety violation: prompt matched restricted pattern.")

        return request


class MiddlewarePipeline:
    """
    Orchestrates sequential execution of AI middleware.
    """

    def __init__(self) -> None:
        self._middlewares: list[AIMiddleware] = []

    def use(self, middleware: AIMiddleware) -> MiddlewarePipeline:
        """Register a middleware into the pipeline. Returns self for chaining."""
        self._middlewares.append(middleware)
        return self

    def execute(
        self,
        request: AIRequest,
        terminal_handler: Callable[[AIRequest], AIResponse],
    ) -> AIResponse:
        """
        Pass request through middleware pipeline, invoke handler, then pass response in reverse.
        """
        current_request = request

        # Process requests in forward order
        for mw in self._middlewares:
            current_request = mw.process_request(current_request)

        # Terminal execution
        start_time = time.perf_counter()
        response = terminal_handler(current_request)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # Ensure latency is attached if not set
        if response.latency_ms == 0.0:
            object.__setattr__(response, "latency_ms", latency_ms)

        # Process responses in reverse order
        current_response = response
        for mw in reversed(self._middlewares):
            current_response = mw.process_response(current_request, current_response)

        return current_response


__all__ = [
    "AIMiddleware",
    "CachingMiddleware",
    "LoggingMiddleware",
    "MiddlewarePipeline",
    "SafetyMiddleware",
    "TelemetryMiddleware",
]
