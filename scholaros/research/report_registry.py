"""
ScholarOS
Report Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Registry for
research reports.
"""

from __future__ import annotations

from scholaros.research.report import (
    Report,
)
from scholaros.research.report_collection import (
    ReportCollection,
)


class ReportRegistry:
    """
    Registry for
    research reports.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        registry.
        """

        self._collection = (
            ReportCollection()
        )

    @property
    def collection(
        self,
    ) -> ReportCollection:
        """
        Return the
        report collection.
        """

        return self._collection

    def register(
        self,
        report: Report,
    ) -> None:
        """
        Register a
        report.
        """

        self._collection.add(
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

        self._collection.remove(
            report,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        registered reports.
        """

        self._collection.clear()

    def reports(
        self,
    ) -> list[
        Report
    ]:
        """
        Return all
        registered reports.
        """

        return (
            self._collection.all()
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of registered
        reports.
        """

        return len(
            self._collection,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        registered reports.
        """

        return iter(
            self._collection,
        )

    def __contains__(
        self,
        report: Report,
    ) -> bool:
        """
        Return whether the
        report is
        registered.
        """

        return (
            report
            in self._collection
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