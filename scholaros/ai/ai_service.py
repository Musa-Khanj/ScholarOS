"""
ScholarOS
AI Service

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
High-level interface for AI operations.

Responsibilities
----------------
• Coordinate prompt execution
• Delegate work to PromptSession
• Provide a stable API for applications
"""

from __future__ import annotations

from scholaros.ai.prompt_session import (
    PromptSession,
)


class AIService:
    """
    High-level AI service.
    """

    def __init__(
        self,
        session: PromptSession,
    ) -> None:

        self._session = session

    def execute(
        self,
        template: str,
        **variables: str,
    ):
        """
        Execute a prompt template using the
        configured PromptSession.
        """

        return self._session.execute(
            template,
            **variables,
        )

    def build(
        self,
        template: str,
        **variables: str,
    ) -> str:
        """
        Build a prompt without executing it.
        """

        return self._session.build(
            template,
            **variables,
        )

    @property
    def session(
        self,
    ) -> PromptSession:
        """
        Return the underlying PromptSession.
        """

        return self._session

    def contains(
        self,
        template: str,
    ) -> bool:
        """
        Returns True if the specified prompt
        template exists.
        """

        return self._session.builder.contains(
            template,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation
        of the AIService.
        """

        return (
            f"{self.__class__.__name__}"
            f"(session={self._session!r})"
        )

    