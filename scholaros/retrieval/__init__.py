"""
ScholarOS Retrieval Subsystem.

Provides unified lexical, semantic, and hybrid information retrieval,
reranking, scoring algorithms, and context construction for ScholarOS.
"""

from __future__ import annotations

from scholaros.retrieval.collection import RetrievalCollection
from scholaros.retrieval.configuration import RetrievalConfiguration
from scholaros.retrieval.context import (
    ContextBuilder,
    RetrievalContext,
    default_token_estimator,
)
from scholaros.retrieval.contracts import (
    ContextBuilderProtocol,
    FilterProtocol,
    PipelineProtocol,
    RerankerProtocol,
    RetrieverProtocol,
    StrategyProtocol,
    VectorRetrieverContract,
)
from scholaros.retrieval.diagnostics import RetrievalDiagnostics
from scholaros.retrieval.events import (
    ContextBuilt,
    RerankingCompleted,
    RerankingStarted,
    RetrievalCompleted,
    RetrievalEvent,
    RetrievalFailed,
    RetrievalStarted,
)
from scholaros.retrieval.exceptions import (
    ContextBuildingError,
    FilterError,
    PipelineExecutionError,
    RerankingError,
    RetrievalConfigurationError,
    RetrievalEmbeddingError,
    RetrievalError,
    RetrieverNotFoundError,
    StrategyExecutionError,
)
from scholaros.retrieval.filters import RetrievalFilter
from scholaros.retrieval.hybrid import HybridRetriever
from scholaros.retrieval.keyword import KeywordRetriever, tokenize
from scholaros.retrieval.loader import RetrievalLoader
from scholaros.retrieval.manager import RetrievalManager
from scholaros.retrieval.metrics import RetrievalMetrics
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.registry import RetrievalRegistry
from scholaros.retrieval.reranker import (
    BaseReranker,
    CrossEncoderReranker,
    LLMReranker,
    RetrievalRanker,
    ScoreReranker,
)
from scholaros.retrieval.result import RetrievalResult
from scholaros.retrieval.retriever import BaseRetriever, Retriever
from scholaros.retrieval.scoring import (
    blend_scores,
    deduplicate_results,
    min_max_normalize,
    reciprocal_rank_fusion,
)
from scholaros.retrieval.semantic import SemanticRetriever, VectorStoreRetriever
from scholaros.retrieval.service import RetrievalService
from scholaros.retrieval.strategies import (
    DelegateStrategy,
    HybridStrategy,
    KeywordStrategy,
    RetrievalStrategy,
    SemanticStrategy,
    StrategyRegistry,
)

__all__ = [
    # Core Models & Legacy
    "RetrievalResult",
    "RetrievalCollection",
    "RetrievalRegistry",
    "RetrievalManager",
    "RetrievalLoader",
    "Retriever",
    "RetrievalFilter",
    "RetrievalRanker",
    "RetrievalPipeline",
    # Query & Context
    "RetrievalQuery",
    "RetrievalContext",
    "ContextBuilder",
    "default_token_estimator",
    # Configuration & Diagnostics & Metrics
    "RetrievalConfiguration",
    "RetrievalMetrics",
    "RetrievalDiagnostics",
    # Service
    "RetrievalService",
    # Contracts & Protocols
    "RetrieverProtocol",
    "RerankerProtocol",
    "FilterProtocol",
    "PipelineProtocol",
    "ContextBuilderProtocol",
    "StrategyProtocol",
    "VectorRetrieverContract",
    # Retrievers
    "BaseRetriever",
    "KeywordRetriever",
    "SemanticRetriever",
    "VectorStoreRetriever",
    "HybridRetriever",
    "tokenize",
    # Strategies
    "RetrievalStrategy",
    "KeywordStrategy",
    "SemanticStrategy",
    "HybridStrategy",
    "DelegateStrategy",
    "StrategyRegistry",
    # Rerankers
    "BaseReranker",
    "ScoreReranker",
    "CrossEncoderReranker",
    "LLMReranker",
    # Scoring & Fusion
    "reciprocal_rank_fusion",
    "min_max_normalize",
    "blend_scores",
    "deduplicate_results",
    # Events
    "RetrievalEvent",
    "RetrievalStarted",
    "RetrievalCompleted",
    "RetrievalFailed",
    "RerankingStarted",
    "RerankingCompleted",
    "ContextBuilt",
    # Exceptions
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
