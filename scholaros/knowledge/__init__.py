"""
ScholarOS Knowledge Subsystem.

Comprehensive knowledge management architecture providing:
- Strongly typed Document, Chunk, Collection, Metadata, and Source models
- Pipeline stages: Load -> Parse -> Normalize -> Chunk -> Store -> Index
- Pluggable storage abstraction (InMemory, SQLite, DuckDB, Vector DBs)
- Unified search engine with BM25, metadata, recency, and composite ranking
- Format adapters (Filesystem, Text, Markdown, JSON, PDF)
- Statistics, diagnostics, and EventBus integration
- Service framework and DI container integration
"""

from __future__ import annotations

from scholaros.knowledge.chunk import Chunk
from scholaros.knowledge.collection import Collection, KnowledgeCollection
from scholaros.knowledge.diagnostics import (
    DiagnosticIssue,
    DiagnosticReport,
    KnowledgeDiagnostics,
)
from scholaros.knowledge.document import Document, KnowledgeDocument
from scholaros.knowledge.events import (
    CollectionCreated,
    CollectionDeleted,
    CollectionIndexed,
    DocumentAdded,
    DocumentRemoved,
    DocumentUpdated,
    KnowledgeEvent,
    SearchCompleted,
)
from scholaros.knowledge.exceptions import (
    ChunkNotFoundError,
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    DocumentNotFoundError,
    DuplicateDocumentError,
    IndexingError,
    IngestionError,
    KnowledgeError,
    ParseError,
    SearchError,
    StorageError,
    ValidationError,
)
from scholaros.knowledge.filters import KnowledgeFilter
from scholaros.knowledge.index import InvertedIndex
from scholaros.knowledge.lifecycle import (
    BatchIngestionResult,
    DocumentStatus,
    DuplicatePolicy,
    IngestionResult,
)
from scholaros.knowledge.loader import KnowledgeLoader, Loader
from scholaros.knowledge.manager import KnowledgeManager, Manager
from scholaros.knowledge.metadata import KnowledgeMetadata, Metadata
from scholaros.knowledge.normalizer import TextNormalizer
from scholaros.knowledge.parser import (
    DocumentParser,
    JSONDocumentParser,
    MarkdownParser,
    PDFDocumentParser,
    ParserRegistry,
    PlainTextParser,
)
from scholaros.knowledge.ranking import (
    BM25Ranker,
    CompositeRanker,
    CosineSimilarityRanker,
    MetadataWeightingRanker,
    RecencyWeightingRanker,
)
from scholaros.knowledge.registry import KnowledgeRegistry, Registry
from scholaros.knowledge.search import (
    SearchEngine,
    SearchQuery,
    SearchResponse,
    SearchResult,
    SearchType,
)
from scholaros.knowledge.serializer import (
    CollectionSerializer,
    DocumentSerializer,
)
from scholaros.knowledge.service import KnowledgeService
from scholaros.knowledge.source import KnowledgeSource, Source
from scholaros.knowledge.statistics import (
    KnowledgeStatistics,
    calculate_statistics,
)
from scholaros.knowledge.storage import (
    InMemoryStorage,
    KnowledgeStorage,
)

__all__ = [
    # Core Models & Aliases
    "BM25Ranker",
    "BatchIngestionResult",
    "Chunk",
    "ChunkNotFoundError",
    "Collection",
    "CollectionAlreadyExistsError",
    "CollectionCreated",
    "CollectionDeleted",
    "CollectionIndexed",
    "CollectionNotFoundError",
    "CollectionSerializer",
    "CompositeRanker",
    "CosineSimilarityRanker",
    "DiagnosticIssue",
    "DiagnosticReport",
    "Document",
    "DocumentAdded",
    "DocumentNotFoundError",
    "DocumentParser",
    "DocumentRemoved",
    "DocumentSerializer",
    "DocumentStatus",
    "DocumentUpdated",
    "DuplicateDocumentError",
    "DuplicatePolicy",
    "InMemoryStorage",
    "IndexingError",
    "IngestionError",
    "IngestionResult",
    "InvertedIndex",
    "JSONDocumentParser",
    "KnowledgeCollection",
    "KnowledgeDiagnostics",
    "KnowledgeDocument",
    "KnowledgeError",
    "KnowledgeEvent",
    "KnowledgeFilter",
    "KnowledgeLoader",
    "KnowledgeManager",
    "KnowledgeMetadata",
    "KnowledgeRegistry",
    "KnowledgeService",
    "KnowledgeSource",
    "KnowledgeStatistics",
    "KnowledgeStorage",
    "Loader",
    "Manager",
    "MarkdownParser",
    "Metadata",
    "MetadataWeightingRanker",
    "PDFDocumentParser",
    "ParseError",
    "ParserRegistry",
    "PlainTextParser",
    "RecencyWeightingRanker",
    "Registry",
    "SearchCompleted",
    "SearchEngine",
    "SearchError",
    "SearchQuery",
    "SearchResponse",
    "SearchResult",
    "SearchType",
    "Source",
    "StorageError",
    "TextNormalizer",
    "ValidationError",
    "calculate_statistics",
]
