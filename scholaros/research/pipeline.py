"""
ScholarOS
Research Pipeline

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Coordinates high-level research workflows.

Responsibilities
----------------
• Coordinate AI-powered research tasks
• Delegate prompt execution to AIService
• Serve as the application entry point for
  research operations
"""

from __future__ import annotations

from scholaros.ai.ai_service import AIService


class ResearchPipeline:
    """
    Coordinates research workflows.
    """

    def __init__(
        self,
        ai: AIService,
    ) -> None:

        self._ai = ai

    def execute(
        self,
        template: str,
        **variables: str,
    ):
        """
        Execute a research prompt using the
        configured AI service.
        """

        return self._ai.execute(
            template,
            **variables,
        )

    def build(
        self,
        template: str,
        **variables: str,
    ) -> str:
        """
        Build a research prompt without
        executing it.
        """

        return self._ai.build(
            template,
            **variables,
        )

    @property
    def ai(
        self,
    ) -> AIService:
        """
        Return the configured AI service.
        """

        return self._ai

    def contains(
        self,
        template: str,
    ) -> bool:
        """
        Returns True if the specified research
        prompt template exists.
        """

        return self._ai.contains(
            template,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation
        of the ResearchPipeline.
        """

        return (
            f"{self.__class__.__name__}"
            f"(ai={self._ai!r})"
        )