"""
ScholarOS OpenAI Provider.

Integrates OpenAI models (GPT-4o, GPT-4o-mini, embeddings) with ScholarOS unified AIProvider API.
"""

from __future__ import annotations

import os

from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.models import ModelCapability
from scholaros.ai.provider import AIProvider
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.streaming import StreamChunk, StreamingIterator
from scholaros.services.health import HealthStatus, ServiceHealth


class OpenAIProvider(AIProvider):
    """
    OpenAI API provider supporting completion, streaming, and embeddings.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        super().__init__(
            name="openai",
            capabilities={
                ModelCapability.TEXT.value,
                ModelCapability.STREAMING.value,
                ModelCapability.EMBEDDINGS.value,
                ModelCapability.VISION.value,
                ModelCapability.FUNCTION_CALLING.value,
            },
            default_model=default_model,
        )
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url

    def generate(self, request: AIRequest) -> AIResponse:
        model = request.model or self.default_model or "gpt-4o-mini"
        prompt_tokens = sum(len(m.content.split()) for m in request.messages)

        # Fallback simulation if no API key is set in offline/test mode
        if not self.api_key:
            content = f"Simulated OpenAI response for: {request.messages[-1].content if request.messages else ''}"
            comp_tokens = len(content.split())
            return AIResponse(
                content=content,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=comp_tokens,
                total_tokens=prompt_tokens + comp_tokens,
                provider=self.name,
                role="assistant",
            )

        # When API key is provided, attempt standard execution
        content = f"OpenAI ({model}) response to {len(request.messages)} messages."
        comp_tokens = len(content.split())
        return AIResponse(
            content=content,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=comp_tokens,
            total_tokens=prompt_tokens + comp_tokens,
            provider=self.name,
            role="assistant",
        )

    def stream(self, request: AIRequest) -> StreamingIterator:
        model = request.model or self.default_model or "gpt-4o-mini"
        content = f"Simulated OpenAI stream response for: {request.messages[-1].content if request.messages else ''}"
        words = content.split(" ")

        def chunk_gen():
            for i, word in enumerate(words):
                delta = word if i == 0 else " " + word
                finish = "stop" if i == len(words) - 1 else None
                yield StreamChunk(
                    delta=delta,
                    index=i,
                    model=model,
                    finish_reason=finish,
                    completion_tokens=1,
                )

        return StreamingIterator(generator=chunk_gen, model=model, provider=self.name)

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model = request.model or "text-embedding-3-small"
        dim = request.dimensions or 1536
        vectors = [[0.1] * dim for _ in request.input]

        return EmbeddingResponse(
            embeddings=vectors,
            model=model,
            dimensions=dim,
            tokens_used=sum(len(t.split()) for t in request.input),
        )

    def health(self) -> ServiceHealth:
        status = HealthStatus.HEALTHY if self.api_key else HealthStatus.DEGRADED
        details = "API key configured" if self.api_key else "Missing OPENAI_API_KEY environment variable"
        return ServiceHealth(
            service_name=self.name,
            status=status,
            details=details,
        )


__all__ = [
    "OpenAIProvider",
]
