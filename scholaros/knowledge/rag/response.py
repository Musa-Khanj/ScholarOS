"""
ScholarOS
RAG Response

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a response produced by
the Retrieval-Augmented Generation
pipeline.
"""

from __future__ import annotations

from typing import Any

from scholaros.knowledge.rag.context import RAGContext
from scholaros.retrieval.result import (
    RetrievalResult,
)


class RAGResponse:
    """
    Represents a RAG response.
    """

    def __init__(
        self,
        content: str,
        model: str,
        results: tuple[
            RetrievalResult,
            ...,
        ] | list[RetrievalResult],
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        context: RAGContext | None = None,
        metadata: dict[str, Any] | None = None,
        latency_ms: float = 0.0,
    ) -> None:
        """
        Initialize the RAG response.
        """

        self._content = content
        self._model = model
        self._results = tuple(results)
        self._prompt_tokens = prompt_tokens
        self._completion_tokens = completion_tokens
        self._total_tokens = total_tokens
        self._context = context
        self._metadata = dict(metadata) if metadata is not None else {}
        self._latency_ms = float(latency_ms)
        if "latency_ms" not in self._metadata and self._latency_ms > 0.0:
            self._metadata["latency_ms"] = self._latency_ms

    @property
    def content(
        self,
    ) -> str:
        """
        Return the generated content.
        """

        return self._content

    @property
    def model(
        self,
    ) -> str:
        """
        Return the model name.
        """

        return self._model

    @property
    def results(
        self,
    ) -> tuple[
        RetrievalResult,
        ...,
    ]:
        """
        Return the retrieval results
        supporting the response.
        """

        return self._results

    @property
    def prompt_tokens(
        self,
    ) -> int:
        """
        Return the number of prompt tokens.
        """

        return self._prompt_tokens

    @property
    def completion_tokens(
        self,
    ) -> int:
        """
        Return the number of completion
        tokens.
        """

        return self._completion_tokens

    @property
    def total_tokens(
        self,
    ) -> int:
        """
        Return the total number of tokens.
        """

        return self._total_tokens

    @property
    def context(self) -> RAGContext:
        """
        Return the RAG context supporting this response.
        """
        if self._context is None:
            self._context = RAGContext(list(self._results))
        return self._context

    @property
    def sources(self) -> tuple[str, ...]:
        """
        Return the unique source names from the retrieval results.
        """
        return self.context.sources

    @property
    def provenance(self) -> tuple[dict[str, Any], ...]:
        """
        Return the retrieval stream provenance records.
        """
        return self.context.provenance

    @property
    def metadata(self) -> dict[str, Any]:
        """
        Return custom response metadata.
        """
        return dict(self._metadata)

    @property
    def latency_ms(self) -> float:
        """
        Return the execution latency in milliseconds.
        """
        return self._latency_ms

    @property
    def has_context(self) -> bool:
        """
        Return True if retrieval results support this response.
        """
        return len(self._results) > 0

    @property
    def query(self) -> str:
        """
        Return the query that originated this response, if available.
        """
        if self._context is not None and self._context.query:
            return self._context.query
        return str(self._metadata.get("query", ""))

    @property
    def attributions(self) -> tuple[dict[str, Any], ...]:
        """
        Return structured citation and attribution records for each retrieved result.
        """
        return self.context.attributions

    def has_source(self, source_name: str) -> bool:
        """
        Return True if the specified source name is present in this response's context.
        """
        return self.context.has_source(source_name)

    @property
    def diagnostics(self) -> dict[str, Any]:
        """
        Return comprehensive execution telemetry and retrieval diagnostics.
        """
        return {
            "query": self.query,
            "strategy": self.metadata.get("strategy", "default"),
            "model": self.model,
            "latency_ms": self.latency_ms,
            "has_context": self.has_context,
            "results_count": len(self._results),
            "sources": list(self.sources),
            "is_truncated": self.context.is_truncated,
            "context_tokens": self.context.token_count,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }

    def __len__(
        self,
    ) -> int:
        """
        Return the number of retrieval
        results supporting the response.
        """

        return len(
            self._results,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the response.
        """

        return (
            f"{self.__class__.__name__}("
            f"model={self.model!r}, "
            f"results={len(self)}"
            f")"
        )
