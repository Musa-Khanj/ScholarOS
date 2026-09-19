"""
ScholarOS Retriever Abstraction.

Defines the BaseRetriever contract for all retrieval backends, strategies, and
the reference collection-based Retriever for backward compatibility.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult

if TYPE_CHECKING:
    from scholaros.retrieval.manager import RetrievalManager


class BaseRetriever(ABC):
    """
    Abstract base retriever contract for ScholarOS.
    """

    def __init__(self, name: str | None = None) -> None:
        self._name = name or self.__class__.__name__

    @property
    def name(self) -> str:
        """Return the unique name of this retriever."""
        return self._name

    @abstractmethod
    def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """
        Execute candidate retrieval given a RetrievalQuery.
        """

    def search(self, query: str, limit: int = 10) -> list[RetrievalResult]:
        """
        Convenience method to query by string text.
        """
        q = RetrievalQuery(text=query, limit=limit)
        return self.retrieve(q)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class Retriever(BaseRetriever):
    """
    Searches registered retrieval collections.
    Maintains full backward-compatibility with legacy API.
    """

    def __init__(
        self,
        manager: RetrievalManager,
        name: str = "CollectionRetriever",
    ) -> None:
        super().__init__(name=name)
        self._manager = manager

    @property
    def manager(self) -> RetrievalManager:
        """Return the retrieval manager."""
        return self._manager

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[RetrievalResult]:
        """Search registered retrieval collections."""
        query_fold = query.casefold()
        matches: list[RetrievalResult] = []

        for collection in self._manager.registry.values():
            for result in collection:
                if query_fold in result.content.casefold():
                    matches.append(result)

        matches.sort(
            key=lambda result: result.score,
            reverse=True,
        )
        return matches

    def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """Execute retrieval adhering to BaseRetriever interface."""
        matches = self.search(query.text)
        if query.min_score > 0.0:
            matches = [m for m in matches if m.score >= query.min_score]
        return matches[: query.limit]

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the retriever."""
        return (
            f"{self.__class__.__name__}("
            f"collections="
            f"{len(self.manager.registry)}"
            f")"
        )


__all__ = [
    "BaseRetriever",
    "Retriever",
]
