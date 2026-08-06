"""
ScholarOS
Report Collection

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Collection of
research reports.
"""

from __future__ import annotations

from scholaros.research.report import (
    Report,
)


class ReportCollection:
    """
    Collection of
    research reports.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the
        collection.
        """

        self._reports: list[
            Report
        ] = []

    def add(
        self,
        report: Report,
    ) -> None:
        """
        Add a
        report.
        """

        self._reports.append(
            report,
        )

    def remove(
        self,
        report: Report,
    ) -> None:
        """
        Remove a
        report.
        """

        self._reports.remove(
            report,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        reports.
        """

        self._reports.clear()

    def all(
        self,
    ) -> list[
        Report
    ]:
        """
        Return all
        reports.
        """

        return list(
            self._reports,
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of reports.
        """

        return len(
            self._reports,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        reports.
        """

        return iter(
            self._reports,
        )

    def __contains__(
        self,
        report: Report,
    ) -> bool:
        """
        Return whether the
        report exists.
        """

        return (
            report
            in self._reports
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