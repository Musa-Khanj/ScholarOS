"""
ScholarOS Reranker Abstraction and Implementations.

Defines the BaseReranker interface and implementations:
- ScoreReranker (sorting by original retrieval score)
- CrossEncoderReranker (cross-attention or text alignment scoring)
- LLMReranker (AIProvider-based zero-shot ranking)
- RetrievalRanker (backward-compatible ranker)
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scholaros.retrieval.exceptions import RerankingError
from scholaros.retrieval.result import RetrievalResult

if TYPE_CHECKING:
    from scholaros.ai.provider import AIProvider


class BaseReranker(ABC):
    """
    Abstract interface for candidate result reranking.
    """

    def __init__(self, name: str | None = None) -> None:
        self._name = name or self.__class__.__name__

    @property
    def name(self) -> str:
        """Return the unique reranker name."""
        return self._name

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_n: int | None = None,
    ) -> list[RetrievalResult]:
        """
        Re-score and re-order retrieval candidates with respect to the query.
        """

    def rank(
        self,
        results: list[RetrievalResult],
        reverse: bool = True,
    ) -> list[RetrievalResult]:
        """Rank results (default implementation sorts by score)."""
        return sorted(results, key=lambda r: r.score, reverse=reverse)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class ScoreReranker(BaseReranker):
    """
    Standard reranker that sorts candidates descending by their existing retrieval score.
    """

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_n: int | None = None,
    ) -> list[RetrievalResult]:
        """Sort candidates by existing score."""
        sorted_results = sorted(results, key=lambda r: r.score, reverse=True)
        if top_n is not None:
            return sorted_results[:top_n]
        return sorted_results


class RetrievalRanker(ScoreReranker):
    """
    Backward-compatible ranker alias for existing test suites.
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class CrossEncoderReranker(BaseReranker):
    """
    Cross-attention style reranker computing joint query-passage lexical/semantic alignment.
    """

    def __init__(
        self,
        length_penalty: float = 0.05,
        name: str = "CrossEncoderReranker",
    ) -> None:
        super().__init__(name=name)
        self.length_penalty = length_penalty

    def _score_pair(self, query: str, content: str) -> float:
        """Compute pair alignment score."""
        q_words = set(re.findall(r"\w+", query.lower()))
        if not q_words:
            return 0.0

        c_words = re.findall(r"\w+", content.lower())
        if not c_words:
            return 0.0

        c_set = set(c_words)
        overlap = len(q_words.intersection(c_set)) / len(q_words)

        # Proximity / exact match boost
        proximity_boost = 0.3 if query.lower() in content.lower() else 0.0

        # Term density
        density = sum(c_words.count(w) for w in q_words) / max(len(c_words), 1)

        raw = (overlap * 0.5) + (proximity_boost * 0.3) + (min(density, 1.0) * 0.2)
        return min(1.0, max(0.0, raw))

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_n: int | None = None,
    ) -> list[RetrievalResult]:
        try:
            reranked: list[RetrievalResult] = []
            for r in results:
                new_score = self._score_pair(query, r.content)
                reranked.append(r.with_rerank_score(round(new_score, 4)))

            reranked.sort(key=lambda r: r.score, reverse=True)
            if top_n is not None:
                return reranked[:top_n]
            return reranked
        except Exception as e:
            raise RerankingError(f"CrossEncoder reranking failed: {e}") from e


class LLMReranker(BaseReranker):
    """
    Uses an AIProvider to evaluate relevance of candidates against the query.
    """

    def __init__(
        self,
        ai_provider: AIProvider | None = None,
        model: str | None = None,
        name: str = "LLMReranker",
    ) -> None:
        super().__init__(name=name)
        self.ai_provider = ai_provider
        self.model = model

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_n: int | None = None,
    ) -> list[RetrievalResult]:
        if not results:
            return []
        if self.ai_provider is None:
            # Graceful fallback to score reranker if no provider configured
            return ScoreReranker().rerank(query, results, top_n=top_n)

        from scholaros.ai.request import AIRequest

        prompt = (
            f"Query: {query}\n\n"
            "Rank the following passages in order of relevance (output highest first):\n"
        )
        for i, r in enumerate(results, 1):
            prompt += f"Passage [{i}]: {r.content[:200]}\n"
        prompt += "\nOutput the passage indices ordered from most to least relevant."

        try:
            req = AIRequest.from_prompt(prompt, model=self.model)
            resp = self.ai_provider.generate(req)
            indices = [int(x) for x in re.findall(r"\b\d+\b", resp.content)]

            seen: set[int] = set()
            ordered: list[RetrievalResult] = []
            for idx in indices:
                if 1 <= idx <= len(results) and idx not in seen:
                    seen.add(idx)
                    # Assign a decay rerank score
                    res = results[idx - 1]
                    decay_score = round(1.0 - (len(ordered) * 0.05), 4)
                    ordered.append(res.with_rerank_score(max(decay_score, 0.01)))

            # Append any unranked candidates
            for i, r in enumerate(results, 1):
                if i not in seen:
                    ordered.append(r.with_rerank_score(0.0))

            if top_n is not None:
                return ordered[:top_n]
            return ordered
        except Exception:
            # Fallback to score reranker on error
            return ScoreReranker().rerank(query, results, top_n=top_n)


__all__ = [
    "BaseReranker",
    "ScoreReranker",
    "RetrievalRanker",
    "CrossEncoderReranker",
    "LLMReranker",
]
