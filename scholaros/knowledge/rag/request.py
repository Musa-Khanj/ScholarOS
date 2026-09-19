"""
ScholarOS
RAG Request

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents a request submitted to
the Retrieval-Augmented Generation
pipeline.
"""

from __future__ import annotations

import math
from typing import Any

from scholaros.retrieval.query import RetrievalQuery


class RAGRequest:
    """
    Represents a RAG request.
    """

    def __init__(
        self,
        query: str,
        minimum_score: float = 0.0,
        strategy: str = "default",
        limit: int = 10,
        collections: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        fallback_on_empty: bool = False,
        empty_fallback_message: str | None = None,
    ) -> None:
        """
        Initialize the RAG request.
        """

        if not isinstance(
            query,
            str,
        ):
            raise TypeError(
                "RAG query must be a string."
            )

        if not query.strip():
            raise ValueError(
                "RAG query must not be empty."
            )

        if not isinstance(
            minimum_score,
            (int, float),
        ):
            raise TypeError(
                "RAG minimum score must "
                "be a number."
            )

        if not math.isfinite(
            float(minimum_score),
        ):
            raise ValueError(
                "RAG minimum score must "
                "be finite."
            )

        if not isinstance(strategy, str):
            raise TypeError("RAG strategy must be a string.")

        if not isinstance(limit, int):
            raise TypeError("RAG limit must be an integer.")

        if limit <= 0:
            raise ValueError("RAG limit must be greater than zero.")

        if collections is not None and not isinstance(collections, (list, tuple)):
            raise TypeError("RAG collections must be a list or tuple of strings.")

        if filters is not None and not isinstance(filters, dict):
            raise TypeError("RAG filters must be a dictionary.")

        if options is not None and not isinstance(options, dict):
            raise TypeError("RAG options must be a dictionary.")

        if max_tokens is not None:
            if not isinstance(max_tokens, int):
                raise TypeError("RAG max_tokens must be an integer.")
            if max_tokens <= 0:
                raise ValueError("RAG max_tokens must be greater than zero.")

        if system_prompt is not None:
            if not isinstance(system_prompt, str):
                raise TypeError("RAG system_prompt must be a string.")
            if not system_prompt.strip():
                raise ValueError("RAG system_prompt must not be blank.")

        if not isinstance(fallback_on_empty, bool):
            raise TypeError("RAG fallback_on_empty must be a boolean.")

        if empty_fallback_message is not None:
            if not isinstance(empty_fallback_message, str):
                raise TypeError("RAG empty_fallback_message must be a string.")
            if not empty_fallback_message.strip():
                raise ValueError("RAG empty_fallback_message must not be blank.")

        self._query = query
        self._minimum_score = float(minimum_score)
        self._strategy = strategy
        self._limit = limit
        self._collections = tuple(collections) if collections is not None else None
        self._filters = dict(filters) if filters is not None else None
        self._options = dict(options) if options is not None else {}
        self._max_tokens = max_tokens
        self._system_prompt = system_prompt
        self._fallback_on_empty = fallback_on_empty
        self._empty_fallback_message = empty_fallback_message

    @property
    def query(
        self,
    ) -> str:
        """
        Return the RAG query.
        """

        return self._query

    @property
    def minimum_score(
        self,
    ) -> float:
        """
        Return the minimum retrieval score.
        """

        return self._minimum_score

    @property
    def strategy(self) -> str:
        """
        Return the targeted retrieval strategy.
        """
        return self._strategy

    @property
    def limit(self) -> int:
        """
        Return the candidate result limit.
        """
        return self._limit

    @property
    def collections(self) -> tuple[str, ...] | None:
        """
        Return the targeted collections, if restricted.
        """
        return self._collections

    @property
    def filters(self) -> dict[str, Any] | None:
        """
        Return the metadata filters, if configured.
        """
        return self._filters

    @property
    def options(self) -> dict[str, Any]:
        """
        Return custom options dictionary.
        """
        return self._options

    @property
    def max_tokens(self) -> int | None:
        """
        Return the optional maximum context token budget.
        """
        return self._max_tokens

    @property
    def system_prompt(self) -> str | None:
        """
        Return the optional custom system prompt.
        """
        return self._system_prompt

    @property
    def fallback_on_empty(self) -> bool:
        """
        Return True if the pipeline should fallback immediately when retrieval returns no context.
        """
        return self._fallback_on_empty

    @property
    def empty_fallback_message(self) -> str | None:
        """
        Return the custom fallback message when retrieval returns no context.
        """
        return self._empty_fallback_message

    def to_retrieval_query(self) -> RetrievalQuery:
        """
        Convert this RAG request into a RetrievalQuery.
        """
        opts = dict(self._options)
        if self._max_tokens is not None and "max_tokens" not in opts:
            opts["max_tokens"] = self._max_tokens
        if self._fallback_on_empty and "fallback_on_empty" not in opts:
            opts["fallback_on_empty"] = True

        return RetrievalQuery(
            text=self._query,
            strategy=self._strategy,
            limit=self._limit,
            min_score=self._minimum_score,
            collections=list(self._collections) if self._collections else [],
            filters=dict(self._filters) if self._filters else {},
            options=opts,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the request.
        """

        if (
            self._strategy == "default"
            and self._limit == 10
            and self._collections is None
            and self._filters is None
            and not self._options
            and self._max_tokens is None
            and self._system_prompt is None
            and not self._fallback_on_empty
            and self._empty_fallback_message is None
        ):
            return (
                f"{self.__class__.__name__}("
                f"query={self.query!r}, "
                f"minimum_score={self.minimum_score!r}"
                f")"
            )

        parts = [
            f"query={self.query!r}",
            f"minimum_score={self.minimum_score!r}",
            f"strategy={self.strategy!r}",
            f"limit={self.limit!r}",
        ]
        if self._max_tokens is not None:
            parts.append(f"max_tokens={self._max_tokens!r}")
        if self._system_prompt is not None:
            parts.append(f"system_prompt={self._system_prompt!r}")
        if self._fallback_on_empty:
            parts.append("fallback_on_empty=True")
        if self._empty_fallback_message is not None:
            parts.append(f"empty_fallback_message={self._empty_fallback_message!r}")

        return f"{self.__class__.__name__}({', '.join(parts)})"
