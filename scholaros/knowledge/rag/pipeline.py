"""
ScholarOS
RAG Pipeline

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Coordinates Retrieval-Augmented
Generation using the existing
retrieval and LLM abstractions.
"""

from __future__ import annotations

from scholaros.ai.llm.base import (
    LLM,
)
from scholaros.ai.llm.message import (
    Message,
    MessageRole,
)
from scholaros.knowledge.rag.context import (
    RAGContext,
)
from scholaros.knowledge.rag.request import (
    RAGRequest,
)
from scholaros.knowledge.rag.response import (
    RAGResponse,
)
from scholaros.retrieval.pipeline import (
    RetrievalPipeline,
)


class RAGPipeline:
    """
    Coordinates the RAG pipeline.
    """

    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
        llm: LLM,
    ) -> None:
        """
        Initialize the RAG pipeline.
        """

        self._retrieval_pipeline = (
            retrieval_pipeline
        )

        self._llm = llm

    @property
    def retrieval_pipeline(
        self,
    ) -> RetrievalPipeline:
        """
        Return the retrieval pipeline.
        """

        return self._retrieval_pipeline

    @property
    def llm(
        self,
    ) -> LLM:
        """
        Return the configured LLM.
        """

        return self._llm

    def run(
        self,
        request: RAGRequest,
    ) -> RAGResponse:
        """
        Execute the RAG pipeline.
        """

        results = (
            self._retrieval_pipeline.run(
                request.query,
                request.minimum_score,
            )
        )

        context = RAGContext(
            results,
        )

        messages = self._build_messages(
            request,
            context,
        )

        response = self._llm.generate(
            messages,
        )

        return RAGResponse(
            content=response.content,
            model=response.model,
            results=context.results,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
        )

    def _build_messages(
        self,
        request: RAGRequest,
        context: RAGContext,
    ) -> list[Message]:
        """
        Build the messages supplied to
        the configured LLM.
        """

        system_content = (
            "You are a research assistant "
            "for ScholarOS. Answer the "
            "user's question using the "
            "provided knowledge context. "
            "If the context does not "
            "contain sufficient information "
            "to answer the question, say so "
            "instead of inventing facts."
        )

        user_content = (
            "Knowledge Context:\n"
            f"{context.text}\n\n"
            "User Question:\n"
            f"{request.query}"
        )

        return [
            Message(
                role=MessageRole.SYSTEM,
                content=system_content,
            ),
            Message(
                role=MessageRole.USER,
                content=user_content,
            ),
        ]

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the pipeline.
        """

        return (
            f"{self.__class__.__name__}("
            f"llm={self.llm!r}"
            f")"
        )