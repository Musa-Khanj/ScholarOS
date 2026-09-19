"""
ScholarOS Knowledge Inverted Index.

Maintains lexical inverted indices for BM25 term matching and chunk retrieval.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable

from scholaros.knowledge.ranking import BM25Ranker

if TYPE_CHECKING:
    from scholaros.knowledge.chunk import Chunk


class InvertedIndex:
    """
    Lexical inverted index with BM25 term weighting.
    """

    def __init__(self, ranker: BM25Ranker | None = None) -> None:
        self.ranker = ranker or BM25Ranker()
        # term -> {chunk_id: term_frequency}
        self._postings: dict[str, dict[str, int]] = defaultdict(dict)
        # chunk_id -> list of tokens
        self._chunk_tokens: dict[str, list[str]] = {}
        # chunk_id -> token count
        self._chunk_lengths: dict[str, int] = {}
        # chunk_id -> chunk metadata
        self._chunk_metadata: dict[str, dict[str, Any]] = {}
        self._total_tokens: int = 0

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Split text into normalized lowercase alphanumeric tokens."""
        return [t.lower() for t in re.findall(r"\b\w+\b", text, re.UNICODE)]

    def add_chunk(self, chunk: Chunk, metadata: dict[str, Any] | None = None) -> None:
        """Index a chunk's content."""
        chunk_id = chunk.identifier
        if chunk_id in self._chunk_tokens:
            self.remove_chunk(chunk_id)

        meta = metadata or dict(chunk.metadata)
        title = meta.get("title", "")
        text_to_index = f"{title} {chunk.content}" if title else chunk.content
        tokens = self.tokenize(text_to_index)
        self._chunk_tokens[chunk_id] = tokens
        self._chunk_lengths[chunk_id] = len(tokens)
        self._chunk_metadata[chunk_id] = meta
        self._total_tokens += len(tokens)

        # Build term frequencies
        for token in tokens:
            self._postings[token][chunk_id] = self._postings[token].get(chunk_id, 0) + 1

    def index_chunk(
        self,
        identifier_or_chunk: str | Chunk,
        content: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Helper to index a chunk by Chunk object or (identifier, content, metadata)."""
        from scholaros.knowledge.chunk import Chunk

        if isinstance(identifier_or_chunk, Chunk):
            self.add_chunk(identifier_or_chunk, metadata=metadata)
        else:
            c = Chunk(identifier=identifier_or_chunk, content=content, metadata=metadata or {})
            self.add_chunk(c, metadata=metadata)

    def remove_chunk(self, chunk_id: str) -> None:
        """Remove a chunk from the inverted index."""
        if chunk_id not in self._chunk_tokens:
            return

        tokens = self._chunk_tokens.pop(chunk_id)
        length = self._chunk_lengths.pop(chunk_id, 0)
        self._chunk_metadata.pop(chunk_id, None)
        self._total_tokens = max(0, self._total_tokens - length)

        for token in set(tokens):
            if token in self._postings:
                self._postings[token].pop(chunk_id, None)
                if not self._postings[token]:
                    del self._postings[token]

    @property
    def total_chunks(self) -> int:
        return len(self._chunk_tokens)

    @property
    def avg_chunk_len(self) -> float:
        if not self._chunk_lengths:
            return 0.0
        return self._total_tokens / len(self._chunk_lengths)

    def search_keyword(
        self,
        query: str,
        limit: int = 10,
        filter_fn: Callable[[dict[str, Any]], bool] | None = None,
    ) -> list[tuple[str, float]]:
        """
        Execute BM25 keyword search, returning sorted list of (chunk_id, score).
        """
        query_terms = self.tokenize(query)
        if not query_terms or not self._chunk_tokens:
            return []

        # Find candidate chunk IDs containing at least one query term
        candidates: set[str] = set()
        for term in query_terms:
            if term in self._postings:
                candidates.update(self._postings[term].keys())

        if not candidates:
            return []

        # Build document frequencies mapping
        doc_freqs: dict[str, int] = {
            term: len(self._postings[term]) for term in query_terms if term in self._postings
        }

        total_docs = len(self._chunk_tokens)
        avg_len = self.avg_chunk_len
        scored: list[tuple[str, float]] = []

        for cid in candidates:
            # Check filter if provided
            if filter_fn and not filter_fn(self._chunk_metadata.get(cid, {})):
                continue

            doc_terms = self._chunk_tokens[cid]
            doc_len = self._chunk_lengths[cid]
            score = self.ranker.score(
                query_terms=query_terms,
                doc_terms=doc_terms,
                doc_len=doc_len,
                avg_doc_len=avg_len,
                doc_freqs=doc_freqs,
                total_docs=total_docs,
            )
            if score > 0.0:
                scored.append((cid, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]

    def clear(self) -> None:
        """Clear the entire index."""
        self._postings.clear()
        self._chunk_tokens.clear()
        self._chunk_lengths.clear()
        self._chunk_metadata.clear()
        self._total_tokens = 0


__all__ = [
    "InvertedIndex",
]
