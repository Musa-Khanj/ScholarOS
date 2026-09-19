"""
ScholarOS Retrieval Filters.

Provides multi-predicate filtering for retrieval results based on minimum score,
collections, document identifiers, metadata criteria, and sources.
"""

from __future__ import annotations

from typing import Any, Sequence

from scholaros.retrieval.query import RetrievalQuery
from scholaros.retrieval.result import RetrievalResult


class RetrievalFilter:
    """
    Filters retrieval results according to score thresholds, metadata,
    collection scoping, and document constraints.
    """

    def filter(
        self,
        results: list[RetrievalResult],
        minimum_score: float = 0.0,
        collections: Sequence[str] | None = None,
        document_ids: Sequence[str] | None = None,
        metadata_filters: dict[str, Any] | None = None,
        sources: Sequence[str] | None = None,
        query: RetrievalQuery | None = None,
    ) -> list[RetrievalResult]:
        """
        Filter retrieval results by score, collection, document ID, source, or metadata.
        Maintains complete backward-compatibility with (results, minimum_score).
        """
        min_score = minimum_score
        target_collections = set(collections) if collections else None
        target_docs = set(document_ids) if document_ids else None
        target_sources = set(sources) if sources else None
        target_meta = dict(metadata_filters) if metadata_filters else {}

        if query is not None:
            if query.min_score > min_score:
                min_score = query.min_score
            if query.collections:
                target_collections = (
                    target_collections.intersection(query.collections)
                    if target_collections is not None
                    else set(query.collections)
                )
            if query.document_ids:
                target_docs = (
                    target_docs.intersection(query.document_ids)
                    if target_docs is not None
                    else set(query.document_ids)
                )
            if query.filters:
                target_meta.update(query.filters)

        filtered: list[RetrievalResult] = []

        for r in results:
            if r.score < min_score:
                continue

            if target_collections is not None:
                if r.collection is None or r.collection not in target_collections:
                    continue

            if target_docs is not None:
                if r.document_id is None or r.document_id not in target_docs:
                    continue

            if target_sources is not None:
                if r.source not in target_sources:
                    continue

            if target_meta:
                match = True
                for k, expected_val in target_meta.items():
                    actual_val = r.metadata.get(k)
                    if isinstance(expected_val, (list, tuple, set)):
                        if actual_val not in expected_val:
                            match = False
                            break
                    elif actual_val != expected_val:
                        match = False
                        break
                if not match:
                    continue

            filtered.append(r)

        return filtered

    def filter_by_score(
        self,
        results: list[RetrievalResult],
        minimum_score: float,
    ) -> list[RetrievalResult]:
        """Convenience method to filter strictly by minimum score."""
        return self.filter(results, minimum_score=minimum_score)

    def filter_by_collection(
        self,
        results: list[RetrievalResult],
        collections: Sequence[str],
    ) -> list[RetrievalResult]:
        """Convenience method to filter by collections."""
        return self.filter(results, collections=collections)

    def filter_by_query(
        self,
        results: list[RetrievalResult],
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        """Filter results using parameters defined on a RetrievalQuery."""
        return self.filter(results, query=query)

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the retrieval filter."""
        return f"{self.__class__.__name__}()"


__all__ = [
    "RetrievalFilter",
]
