"""
ScholarOS
RAG Context

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents the context assembled from
retrieval results for RAG generation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator, Sequence

from scholaros.retrieval.result import (
    RetrievalResult,
)

if TYPE_CHECKING:
    from scholaros.retrieval.context import RetrievalContext


def _estimate_tokens(text: str) -> int:
    """Estimate token count for a given text string (approx 4 chars/token)."""
    return max(1, len(text) // 4) if text else 0


class RAGContext:
    """
    Represents context assembled from
    retrieval results.
    """

    def __init__(
        self,
        results: Sequence[RetrievalResult],
        query: str = "",
        max_tokens: int | None = None,
    ) -> None:
        """
        Initialize the RAG context.
        """
        self._query = query
        self._max_tokens = max_tokens
        self._is_truncated = False

        if max_tokens is not None and max_tokens > 0:
            selected: list[RetrievalResult] = []
            used_tokens = 0
            for r in results:
                # Approximate tokens for this section
                sec_text = f"[Source: {r.source}]\n{r.content}"
                sec_tokens = _estimate_tokens(sec_text)
                if selected and (used_tokens + sec_tokens > max_tokens):
                    self._is_truncated = True
                    break
                selected.append(r)
                used_tokens += sec_tokens
            self._results = tuple(selected)
            if len(selected) < len(results):
                self._is_truncated = True
        else:
            self._results = tuple(
                results,
            )

    @classmethod
    def from_retrieval_context(
        cls,
        retrieval_context: RetrievalContext,
        query: str = "",
    ) -> RAGContext:
        """
        Construct a RAGContext from an existing RetrievalContext.
        """
        q = query or retrieval_context.query
        max_tok = (
            retrieval_context.metadata.get("max_tokens")
            or retrieval_context.metadata.get("token_budget")
        )
        return cls(
            results=retrieval_context.results,
            query=q,
            max_tokens=max_tok if isinstance(max_tok, int) else None,
        )

    @property
    def query(self) -> str:
        """
        Return the query associated with this context.
        """
        return self._query

    @property
    def max_tokens(self) -> int | None:
        """
        Return the token budget, if configured.
        """
        return self._max_tokens

    @property
    def token_count(self) -> int:
        """
        Return the estimated token count of the assembled context.
        """
        return _estimate_tokens(self.text)

    @property
    def is_truncated(self) -> bool:
        """
        Return True if results were truncated due to token budget.
        """
        return self._is_truncated

    @property
    def results(
        self,
    ) -> tuple[
        RetrievalResult,
        ...,
    ]:
        """
        Return the retrieval results
        used to build the context.
        """

        return self._results

    @property
    def sources(self) -> tuple[str, ...]:
        """
        Return ordered unique sources from the retrieval results.
        """
        seen: set[str] = set()
        unique_sources: list[str] = []
        for r in self._results:
            if r.source and r.source not in seen:
                seen.add(r.source)
                unique_sources.append(r.source)
        return tuple(unique_sources)

    @property
    def provenance(self) -> tuple[dict[str, Any], ...]:
        """
        Return all retrieval stream provenance records from result metadata.
        """
        records: list[dict[str, Any]] = []
        for r in self._results:
            prov = r.metadata.get("provenance")
            if prov and isinstance(prov, dict):
                records.append(dict(prov))
        return tuple(records)

    @property
    def metadata(self) -> tuple[dict[str, Any], ...]:
        """
        Return the metadata dictionaries for all retrieval results.
        """
        return tuple(dict(r.metadata) for r in self._results)

    @property
    def attributions(self) -> tuple[dict[str, Any], ...]:
        """
        Return structured citation and attribution records for each retrieved result.
        """
        records: list[dict[str, Any]] = []
        for index, r in enumerate(self._results, start=1):
            records.append(
                {
                    "index": index,
                    "source": r.source,
                    "score": r.score,
                    "collection": r.collection,
                    "chunk_id": r.chunk_id,
                    "document_id": r.document_id,
                    "provenance": dict(r.metadata.get("provenance", {}))
                    if isinstance(r.metadata.get("provenance"), dict)
                    else {},
                    "metadata": dict(r.metadata),
                }
            )
        return tuple(records)

    def has_source(self, source_name: str) -> bool:
        """
        Return True if the specified source name is present in this context.
        """
        return source_name in self.sources

    def get_by_source(self, source_name: str) -> list[RetrievalResult]:
        """
        Return all retrieval results belonging to the specified source.
        """
        return [r for r in self._results if r.source == source_name]

    @property
    def text(
        self,
    ) -> str:
        """
        Return the assembled context text.
        """

        if not self._results:
            return ""

        sections: list[str] = []

        for index, result in enumerate(
            self._results,
            start=1,
        ):
            sections.append(
                (
                    f"[Source {index}: "
                    f"{result.source}]\n"
                    f"{result.content}"
                )
            )

        return "\n\n".join(
            sections,
        )

    def format_with_metadata(
        self,
        include_sources: bool = True,
        include_scores: bool = False,
        include_provenance: bool = False,
    ) -> str:
        """
        Return custom formatted context text with optional source,
        score, and provenance annotations.
        """
        if not self._results:
            return ""

        sections: list[str] = []
        for index, result in enumerate(self._results, start=1):
            header_parts: list[str] = []
            if include_sources:
                header_parts.append(f"Source {index}: {result.source}")
            if include_scores:
                header_parts.append(f"Score: {result.score:.3f}")
            if include_provenance and "provenance" in result.metadata:
                prov = result.metadata["provenance"]
                header_parts.append(f"Provenance: {prov}")

            header = f"[{' | '.join(header_parts)}]\n" if header_parts else ""
            sections.append(f"{header}{result.content}")

        return "\n\n".join(sections)

    def __len__(
        self,
    ) -> int:
        """
        Return the number of retrieval
        results contained in the context.
        """

        return len(
            self._results,
        )

    def __iter__(self) -> Iterator[RetrievalResult]:
        """
        Iterate over the retrieval results contained in this context.
        """
        return iter(self._results)

    def __contains__(self, item: object) -> bool:
        """
        Return True if the item is present in this context.
        """
        return item in self._results

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the context.
        """

        return (
            f"{self.__class__.__name__}("
            f"results={len(self)}"
            f")"
        )
