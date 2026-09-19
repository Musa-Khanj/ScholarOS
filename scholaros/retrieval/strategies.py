"""
ScholarOS Retrieval Strategies.

Encapsulates retrieval workflows into pluggable strategies (Keyword, Semantic, Hybrid)
managed by a centralized StrategyRegistry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scholaros.retrieval.exceptions import RetrieverNotFoundError, StrategyExecutionError
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.retriever import BaseRetriever

if TYPE_CHECKING:
    from scholaros.retrieval.hybrid import HybridRetriever
    from scholaros.retrieval.keyword import KeywordRetriever
    from scholaros.retrieval.semantic import SemanticRetriever


class RetrievalStrategy(ABC):
    """
    Abstract base strategy governing how a query is resolved to candidate results.
    """

    def __init__(self, name: str) -> None:
        self._name = name.strip().lower()

    @property
    def name(self) -> str:
        """Return the strategy name."""
        return self._name

    @abstractmethod
    def execute(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """Execute candidate retrieval according to the strategy."""


class KeywordStrategy(RetrievalStrategy):
    """Lexical keyword search strategy."""

    def __init__(
        self,
        retriever: KeywordRetriever | BaseRetriever,
        name: str = "keyword",
    ) -> None:
        super().__init__(name=name)
        self.retriever = retriever

    def execute(self, query: RetrievalQuery) -> list[RetrievalResult]:
        try:
            return self.retriever.retrieve(query)
        except Exception as e:
            raise StrategyExecutionError(f"Keyword strategy failed: {e}") from e


class SemanticStrategy(RetrievalStrategy):
    """Dense semantic embedding search strategy."""

    def __init__(
        self,
        retriever: SemanticRetriever | BaseRetriever,
        name: str = "semantic",
    ) -> None:
        super().__init__(name=name)
        self.retriever = retriever

    def execute(self, query: RetrievalQuery) -> list[RetrievalResult]:
        try:
            return self.retriever.retrieve(query)
        except Exception as e:
            raise StrategyExecutionError(f"Semantic strategy failed: {e}") from e


class HybridStrategy(RetrievalStrategy):
    """Hybrid fusion search strategy."""

    def __init__(
        self,
        retriever: HybridRetriever | BaseRetriever,
        name: str = "hybrid",
    ) -> None:
        super().__init__(name=name)
        self.retriever = retriever

    def execute(self, query: RetrievalQuery) -> list[RetrievalResult]:
        try:
            return self.retriever.retrieve(query)
        except Exception as e:
            raise StrategyExecutionError(f"Hybrid strategy failed: {e}") from e


class DelegateStrategy(RetrievalStrategy):
    """Delegates query execution to an arbitrary BaseRetriever."""

    def __init__(self, retriever: BaseRetriever, name: str = "delegate") -> None:
        super().__init__(name=name)
        self.retriever = retriever

    def execute(self, query: RetrievalQuery) -> list[RetrievalResult]:
        try:
            return self.retriever.retrieve(query)
        except Exception as e:
            raise StrategyExecutionError(f"Delegate strategy failed: {e}") from e


class StrategyRegistry:
    """
    Registry for managing available retrieval strategies.
    """

    def __init__(self) -> None:
        self._strategies: dict[str, RetrievalStrategy] = {}

    def register(self, name: str, strategy: RetrievalStrategy) -> None:
        """Register a retrieval strategy under a canonical name."""
        self._strategies[name.strip().lower()] = strategy

    def get(self, name: str) -> RetrievalStrategy:
        """Retrieve a strategy by name, raising RetrieverNotFoundError if absent."""
        canonical = name.strip().lower()
        strategy = self._strategies.get(canonical)
        if strategy is None:
            raise RetrieverNotFoundError(f"Retrieval strategy '{name}' is not registered.")
        return strategy

    def contains(self, name: str) -> bool:
        """Check if a strategy is registered."""
        return name.strip().lower() in self._strategies

    def remove(self, name: str) -> bool:
        """Unregister a strategy."""
        canonical = name.strip().lower()
        return self._strategies.pop(canonical, None) is not None

    def list_strategies(self) -> list[str]:
        """Return names of all registered strategies."""
        return sorted(self._strategies.keys())

    def clear(self) -> None:
        """Remove all registered strategies."""
        self._strategies.clear()

    def __len__(self) -> int:
        return len(self._strategies)


__all__ = [
    "RetrievalStrategy",
    "KeywordStrategy",
    "SemanticStrategy",
    "HybridStrategy",
    "DelegateStrategy",
    "StrategyRegistry",
]
