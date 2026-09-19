"""
ScholarOS Knowledge Ranking Strategies.

Implements scoring algorithms: BM25, cosine similarity, metadata weighting,
and recency decay.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any


class BM25Ranker:
    """
    Standard Okapi BM25 relevance scoring algorithm for text matching.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b

    def score(
        self,
        query_terms: list[str],
        doc_terms: list[str],
        doc_len: int,
        avg_doc_len: float,
        doc_freqs: dict[str, int],
        total_docs: int,
    ) -> float:
        """Calculate BM25 score for a document given query terms."""
        if total_docs == 0 or avg_doc_len == 0:
            return 0.0

        # Term counts in document
        tf_map: dict[str, int] = {}
        for t in doc_terms:
            tf_map[t] = tf_map.get(t, 0) + 1

        score = 0.0
        for term in query_terms:
            if term not in tf_map:
                continue

            tf = tf_map[term]
            df = doc_freqs.get(term, 0)

            # IDF calculation with smoothing
            idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)

            # Term saturation
            denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / avg_doc_len))
            numer = tf * (self.k1 + 1.0)
            score += idf * (numer / denom)

        return score


class CosineSimilarityRanker:
    """
    Computes vector cosine similarity between dense embeddings.
    """

    @staticmethod
    def score(vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity score between two float vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        return max(0.0, dot / (norm1 * norm2))

    @staticmethod
    def similarity(vec1: list[float], vec2: list[float]) -> float:
        """Alias for score."""
        return CosineSimilarityRanker.score(vec1, vec2)


class MetadataWeightingRanker:
    """
    Computes a relevance boost based on metadata matches (tags, author, source).
    """

    def __init__(self, tag_boost: float = 0.5, author_boost: float = 0.3) -> None:
        self.tag_boost = tag_boost
        self.author_boost = author_boost

    def score(
        self,
        doc_metadata: dict[str, Any],
        query_tags: list[str] | None = None,
        query_author: str | None = None,
    ) -> float:
        """Calculate metadata boost score."""
        boost = 0.0
        doc_tags = {str(t).lower() for t in doc_metadata.get("tags", [])}

        if query_tags:
            for qt in query_tags:
                if qt.lower() in doc_tags:
                    boost += self.tag_boost

        if query_author:
            doc_author = str(doc_metadata.get("author", "")).lower()
            if query_author.lower() in doc_author:
                boost += self.author_boost

        return boost


class RecencyWeightingRanker:
    """
    Calculates an exponential time-decay boost for recently modified documents.
    """

    def __init__(self, half_life_days: float = 30.0) -> None:
        self.half_life_days = max(1.0, half_life_days)

    def score(self, timestamp: datetime | None) -> float:
        """Calculate recency score (1.0 = current, 0.5 = one half life ago, decays towards 0.0)."""
        if timestamp is None:
            return 0.0

        now = datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        age_days = max(0.0, (now - timestamp).total_seconds() / 86400.0)
        return math.exp(-math.log(2) * (age_days / self.half_life_days))

    def boost(self, timestamp: datetime | None) -> float:
        """Alias for score."""
        return self.score(timestamp)


class CompositeRanker:
    """
    Combines lexical, semantic, metadata, and recency scores with configurable weights.
    """

    def __init__(
        self,
        weight_bm25: float = 0.6,
        weight_semantic: float = 0.2,
        weight_metadata: float = 0.1,
        weight_recency: float = 0.1,
        bm25_weight: float | None = None,
        semantic_weight: float | None = None,
        metadata_weight: float | None = None,
        recency_weight: float | None = None,
    ) -> None:
        self.w_bm25 = bm25_weight if bm25_weight is not None else weight_bm25
        self.w_semantic = semantic_weight if semantic_weight is not None else weight_semantic
        self.w_metadata = metadata_weight if metadata_weight is not None else weight_metadata
        self.w_recency = recency_weight if recency_weight is not None else weight_recency

    def combine(
        self,
        bm25_score: float = 0.0,
        semantic_score: float = 0.0,
        metadata_score: float = 0.0,
        recency_score: float = 0.0,
        recency_boost: float | None = None,
        **kwargs: Any,
    ) -> float:
        """Combine component scores into a single weighted relevance metric."""
        r_score = recency_boost if recency_boost is not None else recency_score
        return (
            self.w_bm25 * bm25_score
            + self.w_semantic * semantic_score
            + self.w_metadata * metadata_score
            + self.w_recency * r_score
        )

    def score(self, *args: Any, **kwargs: Any) -> float:
        """Alias for combine."""
        return self.combine(*args, **kwargs)


__all__ = [
    "BM25Ranker",
    "CompositeRanker",
    "CosineSimilarityRanker",
    "MetadataWeightingRanker",
    "RecencyWeightingRanker",
]
