"""
ScholarOS RAG Exceptions.

Re-exports RAG subsystem exceptions from scholaros.knowledge.exceptions.
"""

from __future__ import annotations

from scholaros.knowledge.exceptions import (
    RAGConfigurationError,
    RAGContextError,
    RAGError,
    RAGGenerationError,
    RAGPipelineError,
    RAGTimeoutError,
)

__all__ = [
    "RAGConfigurationError",
    "RAGContextError",
    "RAGError",
    "RAGGenerationError",
    "RAGPipelineError",
    "RAGTimeoutError",
]
