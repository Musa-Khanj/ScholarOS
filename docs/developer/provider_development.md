# AI Provider Development Guide

ScholarOS provides an extensible AI provider abstraction that allows integrating any large language model, inference endpoint, or embedding provider.

---

## 1. The `AIProvider` Base Contract

All LLM providers inherit from `scholaros.ai.provider.AIProvider`:

```python
from __future__ import annotations
from typing import Any
from scholaros.ai.provider import AIProvider
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.streaming import StreamingIterator
from scholaros.services.health import ServiceHealth, HealthStatus


class CustomInferenceProvider(AIProvider):
    """Integrates a custom internal LLM inference endpoint."""

    def __init__(self, endpoint_url: str = "http://localhost:8080") -> None:
        super().__init__(name="custom_llm", default_model="custom-research-v1")
        self.endpoint_url = endpoint_url

    def generate(self, request: AIRequest) -> AIResponse:
        """Execute synchronous text generation."""
        # Extract prompt or messages
        prompt = request.prompt or "\n".join(m.content for m in request.messages)
        
        # Call custom endpoint (mocked for illustration)
        generated_text = f"Synthesized answer to: {prompt}"
        
        return AIResponse(
            content=generated_text,
            model=request.model or self.default_model,
            usage={"prompt_tokens": len(prompt.split()), "completion_tokens": len(generated_text.split())},
        )

    def stream(self, request: AIRequest) -> StreamingIterator:
        """Execute streaming text generation."""
        # Yield tokens iteratively
        def token_generator():
            words = ["This", " is", " a", " streaming", " response."]
            for word in words:
                yield word
        return StreamingIterator(token_generator())

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate dense vector embeddings."""
        # Generate dummy 384-dimensional unit vectors
        import math
        embeddings = []
        for text in request.texts:
            vec = [1.0 / math.sqrt(384)] * 384
            embeddings.append(vec)
        return EmbeddingResponse(embeddings=embeddings, model=request.model or "custom-embed")

    def health(self) -> ServiceHealth:
        """Perform provider health check."""
        return ServiceHealth(
            service_name=self.name,
            status=HealthStatus.HEALTHY,
            details="Custom inference endpoint reachable.",
        )
```

---

## 2. Registering with `AIManager` and `AIFactory`

You can register your new provider directly with the `AIManager`:

```python
from scholaros.ai.manager import AIManager
from scholaros.ai.client import AIClient

manager = AIManager()
custom_provider = CustomInferenceProvider()

manager.register_provider(custom_provider)
client = AIClient(manager)

# Generate using the custom provider
response = client.generate(
    prompt_or_messages="What is quantum entanglement?",
    model="custom-research-v1",
)
print(response.content)
```

Next Step: Review testing methodologies in the [Testing & Quality Engineering Guide](testing.md).
