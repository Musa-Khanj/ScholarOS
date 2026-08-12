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
        ],
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
    ) -> None:
        """
        Initialize the RAG response.
        """

        self._content = content
        self._model = model
        self._results = results
        self._prompt_tokens = prompt_tokens
        self._completion_tokens = completion_tokens
        self._total_tokens = total_tokens

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