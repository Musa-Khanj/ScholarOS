"""
ScholarOS Retrieval Exceptions.

Defines the exception hierarchy for all retrieval operations, strategies,
rerankers, and context construction errors.
"""

from __future__ import annotations

from scholaros.core.exceptions import ScholarOSError


class RetrievalError(ScholarOSError):
    """Base exception for all retrieval subsystem errors."""


class RetrieverNotFoundError(RetrievalError):
    """Raised when a requested retriever is not found or registered."""


class StrategyExecutionError(RetrievalError):
    """Raised when a retrieval strategy fails during candidate retrieval."""


class RerankingError(RetrievalError):
    """Raised when reranking candidate results fails."""


class FilterError(RetrievalError):
    """Raised when a filter fails or filter conditions are invalid."""


class ContextBuildingError(RetrievalError):
    """Raised when context construction fails or context limits are exceeded."""


class RetrievalConfigurationError(RetrievalError):
    """Raised when retrieval configuration is invalid."""


class RetrievalEmbeddingError(RetrievalError):
    """Raised when generating embeddings for semantic retrieval fails."""


class PipelineExecutionError(RetrievalError):
    """Raised when a retrieval pipeline step fails during execution."""


__all__ = [
    "RetrievalError",
    "RetrieverNotFoundError",
    "StrategyExecutionError",
    "RerankingError",
    "FilterError",
    "ContextBuildingError",
    "RetrievalConfigurationError",
    "RetrievalEmbeddingError",
    "PipelineExecutionError",
]
