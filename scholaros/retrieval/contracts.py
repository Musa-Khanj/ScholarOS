"""
ScholarOS Retrieval Subsystem Contracts.

Re-exports retrieval protocols and interface specifications from scholaros.contracts.retrieval.
"""

from __future__ import annotations

from scholaros.contracts.retrieval import (
    ContextBuilderProtocol,
    FilterProtocol,
    HybridRetrieverContract,
    PipelineProtocol,
    RerankerProtocol,
    RetrieverProtocol,
    StrategyProtocol,
    VectorRetrieverContract,
)

__all__ = [
    "RetrieverProtocol",
    "RerankerProtocol",
    "FilterProtocol",
    "PipelineProtocol",
    "ContextBuilderProtocol",
    "StrategyProtocol",
    "VectorRetrieverContract",
    "HybridRetrieverContract",
]
