"""
ScholarOS
Report Loader

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Loader for
research reports.
"""

from __future__ import annotations

from scholaros.research.report_manager import (
    ReportManager,
)


class ReportLoader:
    """
    Loader for
    research reports.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        loader.
        """

        self._manager = (
            ReportManager()
        )

    @property
    def manager(
        self,
    ) -> ReportManager:
        """
        Return the
        report manager.
        """

        return self._manager

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            "manager="
            f"{self._manager.__class__.__name__}"
            ")"
        )