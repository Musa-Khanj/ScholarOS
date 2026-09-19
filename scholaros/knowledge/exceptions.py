"""
ScholarOS Knowledge Exceptions.

Defines the typed exception hierarchy for the ScholarOS Knowledge subsystem.
"""

from __future__ import annotations

from scholaros.core.exceptions import ScholarOSError


class KnowledgeError(ScholarOSError):
    """Base exception for all knowledge subsystem errors."""


class DocumentNotFoundError(KnowledgeError):
    """Raised when a requested knowledge document is not found."""


class CollectionNotFoundError(KnowledgeError):
    """Raised when a requested knowledge collection is not found."""


class CollectionAlreadyExistsError(KnowledgeError):
    """Raised when attempting to register a collection that already exists."""


class ChunkNotFoundError(KnowledgeError):
    """Raised when a requested chunk is not found."""


class StorageError(KnowledgeError):
    """Raised when an operation on the storage backend fails."""


class ParseError(KnowledgeError):
    """Raised when a document cannot be parsed."""


class SearchError(KnowledgeError):
    """Raised when a search query fails to execute."""


class ValidationError(KnowledgeError):
    """Raised when document, chunk, or metadata validation fails."""


class DuplicateDocumentError(KnowledgeError):
    """Raised when a document is detected as duplicate and policy is ERROR."""


class IngestionError(KnowledgeError):
    """Raised when document ingestion fails."""


class IndexingError(KnowledgeError):
    """Raised when document or chunk indexing fails."""


# ---------------------------------------------------------------------------
# RAG Subsystem Exceptions
# ---------------------------------------------------------------------------


class RAGError(KnowledgeError):
    """Base exception for all RAG subsystem errors."""


class RAGConfigurationError(RAGError):
    """Raised when RAG configuration is invalid."""


class RAGPipelineError(RAGError):
    """Raised when execution of a RAG pipeline fails."""


class RAGTimeoutError(RAGPipelineError):
    """Raised when RAG execution exceeds configured timeout."""


class RAGGenerationError(RAGPipelineError):
    """Raised when LLM generation fails during RAG execution."""


class RAGContextError(RAGPipelineError):
    """Raised when building or packing RAG context fails."""


__all__ = [
    "ChunkNotFoundError",
    "CollectionAlreadyExistsError",
    "CollectionNotFoundError",
    "DocumentNotFoundError",
    "DuplicateDocumentError",
    "IndexingError",
    "IngestionError",
    "KnowledgeError",
    "ParseError",
    "RAGConfigurationError",
    "RAGContextError",
    "RAGError",
    "RAGGenerationError",
    "RAGPipelineError",
    "RAGTimeoutError",
    "SearchError",
    "StorageError",
    "ValidationError",
]
