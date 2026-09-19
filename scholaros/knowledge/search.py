"""
ScholarOS Knowledge Search Engine.

Unified search interface supporting keyword, filtered, semantic, and hybrid queries.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from scholaros.knowledge.filters import KnowledgeFilter
from scholaros.knowledge.index import InvertedIndex
from scholaros.knowledge.ranking import CompositeRanker

if TYPE_CHECKING:
    from scholaros.knowledge.document import KnowledgeDocument
    from scholaros.knowledge.storage import KnowledgeStorage


class SearchType(str, Enum):
    """Supported knowledge search modes."""

    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass(slots=True)
class SearchQuery:
    """
    Search request specification.
    """

    query: str
    search_type: SearchType = SearchType.KEYWORD
    collection_name: str | None = None
    filter: KnowledgeFilter | None = None
    limit: int = 10
    threshold: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class SearchResult:
    """
    A single matched chunk in search results.
    """

    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    document: Any = None


@dataclass(slots=True, frozen=True)
class SearchResponse:
    """
    Complete response returned by the search engine.
    """

    results: list[SearchResult]
    total: int
    query: str
    search_type: str
    latency_ms: float = 0.0

    def __iter__(self):
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)

    def __getitem__(self, index: int) -> SearchResult:
        return self.results[index]


class SearchEngine:
    """
    Unified knowledge search engine coordinating inverted indices, rankers, and storage.
    """

    def __init__(
        self,
        storage: KnowledgeStorage | None = None,
        index: InvertedIndex | None = None,
        ranker: CompositeRanker | None = None,
    ) -> None:
        from scholaros.knowledge.storage import InMemoryStorage

        self.storage: KnowledgeStorage = storage if storage is not None else InMemoryStorage()
        self.index = index or InvertedIndex()
        self.ranker = ranker or CompositeRanker()

    def index_document(self, document: KnowledgeDocument, collection_name: str = "default") -> None:
        """Store and index a document and its chunks."""
        from scholaros.knowledge.metadata import KnowledgeMetadata

        self.storage.save_document(document, collection_name=collection_name)
        for chunk in document.chunks:
            meta = dict(chunk.metadata)
            if hasattr(document, "metadata"):
                m = document.metadata
                if isinstance(m, KnowledgeMetadata):
                    meta.update(m.to_dict())
                elif isinstance(m, dict):
                    meta.update(m)
            self.index.index_chunk(chunk.identifier, chunk.content, meta)

    def search(
        self,
        query: SearchQuery | str,
        collection_name: str | None = None,
        limit: int = 10,
        filter_criteria: KnowledgeFilter | None = None,
        search_type: SearchType = SearchType.KEYWORD,
    ) -> SearchResponse:
        """
        Execute unified knowledge search.
        """
        start_time = time.perf_counter()

        if isinstance(query, str):
            sq = SearchQuery(
                query=query,
                collection_name=collection_name,
                limit=limit,
                filter=filter_criteria,
                search_type=search_type,
            )
        else:
            sq = query

        # Filter function for index
        def filter_fn(meta: dict[str, Any]) -> bool:
            if sq.filter is None:
                return True
            return sq.filter.matches(meta)

        # Keyword matching via InvertedIndex
        scored_pairs = self.index.search_keyword(
            query=sq.query,
            limit=sq.limit,
            filter_fn=filter_fn,
        )

        results: list[SearchResult] = []
        for chunk_id, score in scored_pairs:
            if score < sq.threshold:
                continue

            chunk = self.storage.get_chunk(chunk_id)
            if chunk is not None:
                doc = self.storage.get_document(chunk.document_id)
                results.append(
                    SearchResult(
                        chunk_id=chunk.identifier,
                        document_id=chunk.document_id,
                        content=chunk.content,
                        score=round(score, 4),
                        metadata=chunk.metadata,
                        document=doc,
                    )
                )

        latency = (time.perf_counter() - start_time) * 1000.0
        return SearchResponse(
            results=results,
            total=len(results),
            query=sq.query,
            search_type=sq.search_type.value,
            latency_ms=round(latency, 2),
        )


__all__ = [
    "SearchEngine",
    "SearchQuery",
    "SearchResponse",
    "SearchResult",
    "SearchType",
]
