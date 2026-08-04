"""
ScholarOS
Retrieval Filter

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Filters retrieval
results.
"""

from __future__ import annotations

from scholaros.retrieval.result import (
    RetrievalResult,
)


class RetrievalFilter:
    """
    Filters retrieval
    results.
    """

    def filter(
        self,
        results: list[
            RetrievalResult
        ],
        minimum_score: float = 0.0,
    ) -> list[
        RetrievalResult
    ]:
        """
        Filter retrieval
        results.
        """

        return [
            result
            for result in results
            if (
                result.score
                >= minimum_score
            )
        ]

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        retrieval filter.
        """

        return (
            f"{self.__class__.__name__}()"
        )