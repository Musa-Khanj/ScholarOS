"""
ScholarOS Context Construction.

Builds structured, budget-aware prompt context from retrieval results for
downstream consumption by Agents, LLMs, and prompt pipelines without provider lock-in.
"""

from __future__ import annotations

from typing import Any, Callable

from scholaros.retrieval.result import RetrievalResult


def default_token_estimator(text: str) -> int:
    """Estimate token count for a text string (approximately 4 characters per token)."""
    return max(1, len(text) // 4)


class RetrievalContext:
    """
    Structured context package built from retrieval results.
    """

    def __init__(
        self,
        query: str,
        results: list[RetrievalResult],
        total_tokens: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._query = query
        self._results = list(results)
        self._total_tokens = total_tokens
        self._metadata = dict(metadata) if metadata is not None else {}

    @property
    def query(self) -> str:
        """Return the original query."""
        return self._query

    @property
    def results(self) -> list[RetrievalResult]:
        """Return the list of included retrieval results."""
        return list(self._results)

    @property
    def total_tokens(self) -> int:
        """Return the estimated total token count of the context."""
        return self._total_tokens

    @property
    def metadata(self) -> dict[str, Any]:
        """Return context metadata."""
        return self._metadata

    def sources(self) -> list[str]:
        """Return unique source identifiers included in this context."""
        seen: set[str] = set()
        sources_list: list[str] = []
        for r in self._results:
            if r.source not in seen:
                seen.add(r.source)
                sources_list.append(r.source)
        return sources_list

    def format_as_text(
        self,
        include_sources: bool = True,
        include_metadata: bool = False,
    ) -> str:
        """
        Format the retrieved results as clean structured text suitable for LLM prompts.
        """
        if not self._results:
            return ""

        parts: list[str] = []
        for i, res in enumerate(self._results, 1):
            header = f"[{i}]"
            if include_sources:
                header += f" (Source: {res.source})"
            if include_metadata and res.metadata:
                meta_str = ", ".join(f"{k}={v}" for k, v in res.metadata.items())
                header += f" [{meta_str}]"
            parts.append(f"{header}\n{res.content.strip()}")

        return "\n\n".join(parts)

    def format_as_messages(
        self,
        role: str = "system",
        prefix: str = "Relevant context:\n\n",
    ) -> list[dict[str, str]]:
        """
        Format context as chat message dictionaries for LLM requests.
        """
        formatted_text = self.format_as_text()
        if not formatted_text:
            return []
        return [{"role": role, "content": f"{prefix}{formatted_text}"}]

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary representation."""
        return {
            "query": self._query,
            "results": [r.to_dict() for r in self._results],
            "total_tokens": self._total_tokens,
            "metadata": self._metadata,
            "sources": self.sources(),
        }

    def __len__(self) -> int:
        return len(self._results)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"query={self._query!r}, "
            f"items={len(self._results)}, "
            f"tokens={self._total_tokens}"
            f")"
        )


class ContextBuilder:
    """
    Constructs a RetrievalContext from results while enforcing token budgets.
    """

    def __init__(
        self,
        token_budget: int = 4000,
        token_estimator: Callable[[str], int] | None = None,
    ) -> None:
        self.token_budget = token_budget
        self._token_estimator = token_estimator or default_token_estimator

    def build(
        self,
        query: str,
        results: list[RetrievalResult],
        max_tokens: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RetrievalContext:
        """
        Pack results up to the token budget.
        """
        budget = max_tokens if max_tokens is not None else self.token_budget
        selected: list[RetrievalResult] = []
        total_tokens = 0

        for res in results:
            est_tokens = self._token_estimator(res.content)
            if selected and (total_tokens + est_tokens > budget):
                # Cannot fit further results without exceeding budget
                break
            selected.append(res)
            total_tokens += est_tokens
            if total_tokens >= budget:
                break

        return RetrievalContext(
            query=query,
            results=selected,
            total_tokens=total_tokens,
            metadata=metadata,
        )


__all__ = [
    "RetrievalContext",
    "ContextBuilder",
    "default_token_estimator",
]
