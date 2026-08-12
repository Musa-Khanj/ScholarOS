"""
ScholarOS
UI Integration

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides the integration boundary between the
ScholarOS UI components.

The integration layer coordinates the existing
UI application, presentation, and frontend
components.

It does not implement research, RAG, AI,
knowledge, or kernel behavior.
"""

from __future__ import annotations

from scholaros.ui.application import (
    UIApplication,
)
from scholaros.ui.frontend import (
    ScholarOSFrontend,
)
from scholaros.ui.presentation import (
    UIPresentation,
)


class UIIntegration:
    """
    Provides the integration boundary for
    the ScholarOS user interface.

    The integration layer connects the
    application, presentation, and frontend
    layers while preserving the existing
    ScholarOS architecture.
    """

    def __init__(
        self,
        application: UIApplication,
        root: object | None = None,
    ) -> None:
        """
        Initialize the UI integration layer.

        Parameters
        ----------
        application:
            Configured ScholarOS UI application.

        root:
            Optional frontend root object.
        """

        self._application = application

        self._presentation = (
            UIPresentation(
                application,
            )
        )

        self._frontend = (
            ScholarOSFrontend(
                self._presentation,
                root,
            )
        )

    @property
    def application(
        self,
    ) -> UIApplication:
        """
        Return the underlying UI application.
        """

        return self._application

    @property
    def presentation(
        self,
    ) -> UIPresentation:
        """
        Return the UI presentation layer.
        """

        return self._presentation

    @property
    def frontend(
        self,
    ) -> ScholarOSFrontend:
        """
        Return the UI frontend.
        """

        return self._frontend

    def status(
        self,
    ) -> str:
        """
        Return the current UI status.
        """

        return self.presentation.status()

    def info(
        self,
    ) -> dict[str, object]:
        """
        Return UI integration information.
        """

        return {
            "application": self.application,
            "presentation": self.presentation,
            "frontend": self.frontend,
            "status": self.status(),
        }

    def refresh(
        self,
    ) -> None:
        """
        Refresh the frontend state.
        """

        self.frontend.refresh()

    def run(
        self,
    ) -> object:
        """
        Run the integrated frontend.

        Returns
        -------
        object
            The frontend execution result.
        """

        return self.frontend.run()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the UI integration.
        """

        return (
            f"{self.__class__.__name__}("
            f"application={self.application!r}, "
            f"presentation={self.presentation!r}, "
            f"frontend={self.frontend!r}"
            f")"
        )