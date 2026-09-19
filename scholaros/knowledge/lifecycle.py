"""Document lifecycle states, duplicate policies, and ingestion results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scholaros.knowledge.document import KnowledgeDocument


class DocumentStatus(str, Enum):
    """Lifecycle status of a document within the knowledge system."""

    DRAFT = "draft"
    PARSED = "parsed"
    CHUNKED = "chunked"
    EMBEDDED = "embedded"
    INDEXED = "indexed"
    FAILED = "failed"
    ARCHIVED = "archived"


class DuplicatePolicy(str, Enum):
    """Policy for handling duplicate documents during ingestion."""

    REPLACE = "replace"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class IngestionResult:
    """Result of ingesting a single document."""

    document: KnowledgeDocument | None = None
    chunks_count: int = 0
    embedded: bool = False
    indexed: bool = False
    status: DocumentStatus = DocumentStatus.INDEXED
    error: str | None = None
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """Return True if ingestion succeeded."""
        return self.error is None and self.document is not None


@dataclass
class BatchIngestionResult:
    """Result of ingesting a batch or directory of documents."""

    total_files: int = 0
    succeeded: list[KnowledgeDocument] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)
    results: list[IngestionResult] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def success_count(self) -> int:
        """Return count of successfully ingested documents."""
        return len(self.succeeded)

    @property
    def failure_count(self) -> int:
        """Return count of failed document ingestions."""
        return len(self.failed)
