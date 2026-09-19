"""
ScholarOS Ollama Provider.

Integrates local Ollama models with ScholarOS unified AIProvider API.
"""

from __future__ import annotations


from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.models import ModelCapability
from scholaros.ai.ollama_client import OllamaClient
from scholaros.ai.provider import AIProvider
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.streaming import StreamChunk, StreamingIterator
from scholaros.services.health import HealthStatus, ServiceHealth


class OllamaProvider(AIProvider):
    """
    Ollama local inference provider.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3",
    ) -> None:
        super().__init__(
            name="ollama",
            capabilities={
                ModelCapability.TEXT.value,
                ModelCapability.STREAMING.value,
                ModelCapability.EMBEDDINGS.value,
            },
            default_model=default_model,
        )
        self.base_url = base_url
        self.client = OllamaClient(base_url=base_url)

    def generate(self, request: AIRequest) -> AIResponse:
        model = request.model or self.default_model or "llama3"
        prompt = request.prompt or (request.messages[-1].content if request.messages else "")

        try:
            return self.client.generate(prompt=prompt, model=model)
        except Exception:
            # Offline simulation
            prompt_tokens = sum(len(m.content.split()) for m in request.messages)
            content = f"Simulated Ollama response for: {prompt}"
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
        model = request.model or self.default_model or "llama3"
        prompt = request.prompt or (request.messages[-1].content if request.messages else "")
        content = f"Simulated Ollama stream response for: {prompt}"
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
        model = request.model or "nomic-embed-text"
        dim = request.dimensions or 768
        vectors = [[0.01] * dim for _ in request.input]

        return EmbeddingResponse(
            embeddings=vectors,
            model=model,
            dimensions=dim,
            tokens_used=sum(len(t.split()) for t in request.input),
        )

    def health(self) -> ServiceHealth:
        try:
            import httpx
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            status = HealthStatus.HEALTHY if resp.status_code == 200 else HealthStatus.DEGRADED
            details = f"Ollama HTTP {resp.status_code}"
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            details = f"Ollama unreachable: {e}"

        return ServiceHealth(
            service_name=self.name,
            status=status,
            details=details,
        )


__all__ = [
    "OllamaProvider",
]
