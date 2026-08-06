"""
ScholarOS
Report Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manager for
research reports.
"""

from __future__ import annotations

from scholaros.research.citation import (
    Citation,
)
from scholaros.research.report import (
    Report,
)
from scholaros.research.report_registry import (
    ReportRegistry,
)


class ReportManager:
    """
    Manager for
    research reports.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        manager.
        """

        self._registry = (
            ReportRegistry()
        )

    @property
    def registry(
        self,
    ) -> ReportRegistry:
        """
        Return the
        report registry.
        """

        return self._registry

    def create(
        self,
        title: str,
        content: str,
        citations: list[
            Citation
        ] | None = None,
        created_at: str | None = None,
    ) -> Report:
        """
        Create and register
        a report.
        """

        report = Report(
            title=title,
            content=content,
            citations=(
                citations
                if citations is not None
                else []
            ),
            created_at=created_at,
        )

        self.register(
            report,
        )

        return report

    def register(
        self,
        report: Report,
    ) -> None:
        """
        Register a
        report.
        """

        self._registry.register(
            report,
        )

    def unregister(
        self,
        report: Report,
    ) -> None:
        """
        Unregister a
        report.
        """

        self._registry.unregister(
            report,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        reports.
        """

        self._registry.clear()

    def reports(
        self,
    ) -> list[
        Report
    ]:
        """
        Return all
        reports.
        """

        return (
            self._registry.reports()
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of reports.
        """

        return len(
            self._registry,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        reports.
        """

        return iter(
            self._registry,
        )

    def __contains__(
        self,
        report: Report,
    ) -> bool:
        """
        Return whether the
        report is managed.
        """

        return (
            report
            in self._registry
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"size={len(self)}"
            f")"
        )