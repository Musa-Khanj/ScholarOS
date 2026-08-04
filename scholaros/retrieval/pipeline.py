"""
ScholarOS
Retrieval Pipeline

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Coordinates the
retrieval pipeline.
"""

from __future__ import annotations

from scholaros.retrieval.filter import (
    RetrievalFilter,
)
from scholaros.retrieval.ranker import (
    RetrievalRanker,
)
from scholaros.retrieval.result import (
    RetrievalResult,
)
from scholaros.retrieval.retriever import (
    Retriever,
)


class RetrievalPipeline:
    """
    Coordinates the
    retrieval pipeline.
    """

    def __init__(
        self,
        retriever: Retriever,
        retrieval_filter: RetrievalFilter,
        ranker: RetrievalRanker,
    ) -> None:
        """
        Initialize the
        retrieval pipeline.
        """

        self._retriever = retriever
        self._filter = retrieval_filter
        self._ranker = ranker

    @property
    def retriever(
        self,
    ) -> Retriever:
        """
        Return the
        retriever.
        """

        return self._retriever

    @property
    def filter(
        self,
    ) -> RetrievalFilter:
        """
        Return the
        retrieval filter.
        """

        return self._filter

    @property
    def ranker(
        self,
    ) -> RetrievalRanker:
        """
        Return the
        retrieval ranker.
        """

        return self._ranker

    def run(
        self,
        query: str,
        minimum_score: float = 0.0,
    ) -> list[
        RetrievalResult
    ]:
        """
        Execute the
        retrieval pipeline.
        """

        results = (
            self._retriever.search(
                query,
            )
        )

        results = (
            self._filter.filter(
                results,
                minimum_score,
            )
        )

        return self._ranker.rank(
            results,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        retrieval pipeline.
        """

        return (
            f"{self.__class__.__name__}("
            f"collections="
            f"{len(self.retriever.manager.registry)}"
            f")"
        )