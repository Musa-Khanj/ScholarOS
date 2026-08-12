"""
ScholarOS
UI Presentation

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides presentation-facing operations for
the ScholarOS user interface.

The presentation layer translates application
results into simple UI-consumable values.

It does not implement research, RAG, AI,
knowledge, or kernel behavior.
"""

from __future__ import annotations

from typing import Any

from scholaros.ui.application import (
    UIApplication,
)


class UIPresentation:
    """
    Provides presentation-facing operations
    for ScholarOS.

    The presentation layer delegates all
    application behavior to UIApplication
    and exposes UI-friendly values.
    """

    def __init__(
        self,
        application: UIApplication,
    ) -> None:
        """
        Initialize the UI presentation layer.
        """

        self._application = application

    @property
    def application(
        self,
    ) -> UIApplication:
        """
        Return the underlying UI application.
        """

        return self._application

    def status(
        self,
    ) -> str:
        """
        Return the current application status.
        """

        return self.application.status()

    def info(
        self,
    ) -> dict[str, Any]:
        """
        Return application information.
        """

        return self.application.info()

    def research_execute(
        self,
        template: str,
        **variables: str,
    ) -> Any:
        """
        Execute a research operation and return
        the application result.
        """

        return self.application.research_execute(
            template,
            **variables,
        )

    def research_build(
        self,
        template: str,
        **variables: str,
    ) -> str:
        """
        Build a research prompt without
        executing it.
        """

        return self.application.research_build(
            template,
            **variables,
        )

    def research_contains(
        self,
        template: str,
    ) -> bool:
        """
        Return whether a research template
        exists.
        """

        return self.application.research_contains(
            template,
        )

    def rag_query(
        self,
        query: str,
        minimum_score: float = 0.0,
    ) -> Any:
        """
        Execute a RAG query and return the
        resulting response.
        """

        return self.application.rag_query(
            query,
            minimum_score,
        )

    def render_status(
        self,
    ) -> str:
        """
        Return a presentation-ready status
        string.
        """

        return (
            f"ScholarOS status: "
            f"{self.status()}"
        )

    def render_info(
        self,
    ) -> str:
        """
        Return application information as
        presentation-ready text.
        """

        information = self.info()

        return (
            "ScholarOS\n"
            f"Research: "
            f"{'AVAILABLE' if information['research'] else 'UNAVAILABLE'}\n"
            f"RAG: "
            f"{'AVAILABLE' if information['rag'] else 'UNAVAILABLE'}\n"
            f"Status: {information['status']}"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the presentation
        layer.
        """

        return (
            f"{self.__class__.__name__}("
            f"application={self.application!r}"
            f")"
        )