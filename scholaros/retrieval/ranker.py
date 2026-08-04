"""
ScholarOS
Retrieval Ranker

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Ranks retrieval
results.
"""

from __future__ import annotations

from scholaros.retrieval.result import (
    RetrievalResult,
)


class RetrievalRanker:
    """
    Ranks retrieval
    results.
    """

    def rank(
        self,
        results: list[
            RetrievalResult
        ],
        reverse: bool = True,
    ) -> list[
        RetrievalResult
    ]:
        """
        Rank retrieval
        results.
        """

        return sorted(
            results,
            key=lambda result: (
                result.score
            ),
            reverse=reverse,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        retrieval ranker.
        """

        return (
            f"{self.__class__.__name__}()"
        )