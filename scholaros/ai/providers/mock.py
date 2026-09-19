"""
ScholarOS Mock AI Provider.

Provides deterministic responses, simulated streaming, and vector embeddings for testing.
"""

from __future__ import annotations

import math

from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.models import ModelCapability
from scholaros.ai.provider import AIProvider
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.streaming import StreamChunk, StreamingIterator
from scholaros.services.health import HealthStatus, ServiceHealth


class MockProvider(AIProvider):
    """
    Mock AI Provider for automated tests and offline simulation.
    """

    def __init__(
        self,
        name: str = "mock",
        default_response: str = "Mock response from ScholarOS AI.",
        dimensions: int = 128,
        healthy: bool = True,
    ) -> None:
        super().__init__(
            name=name,
            capabilities={
                ModelCapability.TEXT.value,
                ModelCapability.STREAMING.value,
                ModelCapability.EMBEDDINGS.value,
                ModelCapability.FUNCTION_CALLING.value,
            },
            default_model="mock-model",
        )
        self.default_response = default_response
        self.dimensions = dimensions
        self.is_healthy = healthy
        self.call_count: int = 0
        self.last_request: AIRequest | None = None

    def generate(self, request: AIRequest) -> AIResponse:
        self.call_count += 1
        self.last_request = request

        # If custom canned response is in request metadata
        content = request.metadata.get("canned_response", self.default_response)
        model = request.model or self.default_model or "mock-model"

        prompt_tokens = sum(len(m.content.split()) for m in request.messages)
        completion_tokens = len(content.split())

        return AIResponse(
            content=content,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            provider=self.name,
            role="assistant",
            latency_ms=10.0,
        )

    def stream(self, request: AIRequest) -> StreamingIterator:
        self.call_count += 1
        self.last_request = request
        content = request.metadata.get("canned_response", self.default_response)
        model = request.model or self.default_model or "mock-model"
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
        self.call_count += 1
        model = request.model or "mock-embed"
        dim = request.dimensions or self.dimensions

        vectors: list[list[float]] = []
        for text in request.input:
            # Deterministic pseudo-embedding based on character codes
            base_val = sum(ord(c) for c in text) % 1000
            vec = [math.sin(base_val + i) for i in range(dim)]
            # Normalize vector
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            vectors.append([x / norm for x in vec])

        return EmbeddingResponse(
            embeddings=vectors,
            model=model,
            dimensions=dim,
            tokens_used=sum(len(t.split()) for t in request.input),
        )

    def health(self) -> ServiceHealth:
        status = HealthStatus.HEALTHY if self.is_healthy else HealthStatus.UNHEALTHY
        return ServiceHealth(
            service_name=self.name,
            status=status,
            details=f"Mock provider status: {status.name}",
        )


__all__ = [
    "MockProvider",
]
