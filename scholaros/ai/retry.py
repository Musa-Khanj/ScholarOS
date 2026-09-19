"""
ScholarOS AI Retry and Failover Policies.

Provides automatic retries with exponential backoff and multi-provider failover chains.
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from scholaros.ai.exceptions import (
    AIRequestTimeoutError,
    AuthenticationError,
    ProviderError,
    RateLimitError,
)

if TYPE_CHECKING:
    from scholaros.ai.provider import AIProvider

T = TypeVar("T")


class RetryPolicy:
    """
    Exponential backoff retry policy for transient AI provider failures.
    """

    def __init__(
        self,
        max_retries: int = 2,
        initial_delay: float = 0.1,
        max_delay: float = 2.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple[type[Exception], ...] | None = None,
    ) -> None:
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (
            RateLimitError,
            TimeoutError,
            ConnectionError,
            ProviderError,
        )

    def execute(self, operation: Callable[[], T]) -> T:
        """
        Execute an operation with exponential backoff on retryable failures.
        """
        attempt = 0
        delay = self.initial_delay

        while True:
            try:
                return operation()
            except Exception as e:
                # Never retry authentication errors
                if isinstance(e, AuthenticationError):
                    raise

                if not isinstance(e, self.retryable_exceptions) or attempt >= self.max_retries:
                    raise

                attempt += 1
                sleep_time = min(delay, self.max_delay)
                if self.jitter:
                    sleep_time = sleep_time * (0.5 + random.random() * 0.5)

                time.sleep(sleep_time)
                delay *= self.backoff_factor


class FailoverChain:
    """
    Orchestrates sequential provider failover when a primary provider fails.
    """

    def __init__(
        self,
        providers: list[AIProvider],
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        if not providers:
            raise ValueError("FailoverChain requires at least one provider.")
        self.providers = list(providers)
        self.retry_policy = retry_policy or RetryPolicy()

    def execute(self, operation: Callable[[AIProvider], T]) -> tuple[T, AIProvider]:
        """
        Attempt execution on providers in priority order.

        Returns
        -------
        tuple[T, AIProvider]
            The successful operation result and the provider that completed it.
        """
        errors: list[tuple[str, Exception]] = []

        for provider in self.providers:
            try:
                result = self.retry_policy.execute(lambda: operation(provider))
                return result, provider
            except Exception as e:
                errors.append((provider.name, e))

        error_summary = "; ".join(f"{name}: {err}" for name, err in errors)
        if errors and all(isinstance(err, TimeoutError) for _, err in errors):
            raise AIRequestTimeoutError(
                f"All providers in failover chain failed: {error_summary}",
                provider_name=errors[-1][0],
            )
        raise ProviderError(f"All providers in failover chain failed: {error_summary}")


__all__ = [
    "FailoverChain",
    "RetryPolicy",
]
