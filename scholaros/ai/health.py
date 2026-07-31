"""
ScholarOS
AI Health

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents the health status of the AI subsystem.

Responsibilities
----------------
• Store health information
• Report availability
• Provide diagnostic summaries
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AIHealth:
    """
    Represents the health of an AI provider.
    """

    available: bool

    provider: str

    model: str

    message: str = ""

    @property
    def healthy(self) -> bool:
        """
        Returns whether the provider is healthy.
        """

        return self.available

class AIHealthChecker:
    """
    Performs health checks for the AI subsystem.
    """

    def __init__(
        self,
        provider: str,
        model: str,
    ) -> None:

        self._provider = provider
        self._model = model

    @property
    def provider(self) -> str:
        """
        Returns the configured provider.
        """

        return self._provider

    @property
    def model(self) -> str:
        """
        Returns the configured model.
        """

        return self._model

    def check(self) -> AIHealth:
        """
        Execute a health check for the configured
        AI provider.
        """

        try:

            self._probe()

            return AIHealth(
                available=True,
                provider=self._provider,
                model=self._model,
                message="AI provider is healthy.",
            )

        except Exception as exc:

            return AIHealth(
                available=False,
                provider=self._provider,
                model=self._model,
                message=str(exc),
            )

    def _probe(self) -> None:
        """
        Probe the configured AI provider.

        Subclasses may override this method to
        implement provider-specific diagnostics.
        """

        return None

    