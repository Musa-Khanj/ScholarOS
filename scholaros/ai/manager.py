"""
ScholarOS AI Manager.

High-level orchestrator for the ScholarOS AI subsystem, responsible for:
- Model routing and provider selection
- Dynamic failover and automatic retry policies
- Middleware pipeline execution
- Event publishing to the EventBus
- Streaming and embedding dispatch
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from scholaros.ai.cache import ResponseCache
from scholaros.ai.embedding import EmbeddingRequest, EmbeddingResponse
from scholaros.ai.exceptions import (
    AIRequestTimeoutError,
    ProviderNotFoundError,
)
from scholaros.ai.metrics import AIMetrics
from scholaros.ai.middleware import (
    CachingMiddleware,
    LoggingMiddleware,
    MiddlewarePipeline,
    TelemetryMiddleware,
)
from scholaros.ai.models import (
    KNOWN_MODELS,
    ModelCapability,
    ModelSpec,
    ModelTier,
    get_model_spec,
)
from scholaros.ai.registry import ProviderRegistry
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.retry import FailoverChain, RetryPolicy
from scholaros.ai.streaming import StreamingIterator
from scholaros.events.event import Event
from scholaros.services.health import HealthStatus, ServiceHealth

if TYPE_CHECKING:
    from scholaros.ai.llm.base import LLM
    from scholaros.ai.provider import AIProvider
    from scholaros.ai.session import AISession
    from scholaros.events.bus import EventBus


# ---------------------------------------------------------------------------
# 12. AI Lifecycle and Execution Events
# ---------------------------------------------------------------------------


class AIEvent(Event):
    """Base class for all AI subsystem events."""

    def __init__(
        self,
        name: str | None = None,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        event_name = name or self.__class__.__name__
        super().__init__(
            name=event_name,
            payload=payload if payload is not None else {},
            metadata=metadata if metadata is not None else {},
            **kwargs,
        )


class AIRequestStarted(AIEvent):
    """Published when an AI inference request starts."""

    def __init__(self, model: str | None, provider: str | None, **kwargs: Any) -> None:
        super().__init__(payload={"model": model, "provider": provider}, **kwargs)


class AIRequestCompleted(AIEvent):
    """Published when an AI inference request finishes successfully."""

    def __init__(
        self,
        model: str,
        provider: str,
        tokens: int,
        latency_ms: float,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            payload={
                "model": model,
                "provider": provider,
                "tokens": tokens,
                "latency_ms": latency_ms,
            },
            **kwargs,
        )


class AIRequestFailed(AIEvent):
    """Published when an AI request encounters an error."""

    def __init__(self, model: str | None, provider: str | None, error: str, **kwargs: Any) -> None:
        super().__init__(
            payload={"model": model, "provider": provider, "error": error},
            **kwargs,
        )


class AIProviderChanged(AIEvent):
    """Published when a failover or manual provider switch occurs."""

    def __init__(self, previous_provider: str, new_provider: str, reason: str, **kwargs: Any) -> None:
        super().__init__(
            payload={
                "previous_provider": previous_provider,
                "new_provider": new_provider,
                "reason": reason,
            },
            **kwargs,
        )


class AIStreamStarted(AIEvent):
    """Published when token streaming initiates."""

    def __init__(self, model: str, provider: str, **kwargs: Any) -> None:
        super().__init__(payload={"model": model, "provider": provider}, **kwargs)


class AIStreamCompleted(AIEvent):
    """Published when token streaming terminates."""

    def __init__(self, model: str, provider: str, total_tokens: int, **kwargs: Any) -> None:
        super().__init__(
            payload={"model": model, "provider": provider, "total_tokens": total_tokens},
            **kwargs,
        )


# ---------------------------------------------------------------------------
# 2. AI Manager Implementation
# ---------------------------------------------------------------------------


class AIManager:
    """
    Central orchestration engine for ScholarOS AI operations.
    """

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        default_provider: str | None = None,
        retry_policy: RetryPolicy | None = None,
        event_bus: EventBus | None = None,
        metrics: AIMetrics | None = None,
        cache: ResponseCache | None = None,
    ) -> None:
        self.registry = registry if registry is not None else ProviderRegistry()
        self.default_provider = default_provider
        self.retry_policy = retry_policy if retry_policy is not None else RetryPolicy()
        self.event_bus = event_bus
        self.metrics = metrics if metrics is not None else AIMetrics()
        self.cache = cache if cache is not None else ResponseCache()

        # Build standard middleware pipeline
        self.pipeline = MiddlewarePipeline()
        self.pipeline.use(LoggingMiddleware())
        self.pipeline.use(TelemetryMiddleware(self.metrics))
        self.pipeline.use(CachingMiddleware(self.cache))

    def register_provider(
        self,
        provider: AIProvider,
        default: bool = False,
        models: list[str] | None = None,
    ) -> None:
        """Register a provider instance with the manager."""
        self.registry.register(provider, models=models)
        if default or self.default_provider is None:
            self.default_provider = provider.name

    def select_provider(
        self,
        model: str | None = None,
        capability: str | None = None,
        requested_provider: str | None = None,
    ) -> AIProvider:
        """
        Route request to the most appropriate provider based on model, capability, or explicit selection.
        """
        # 1. Explicit provider requested
        if requested_provider:
            canonical = requested_provider.strip().lower()
            if self.registry.contains(canonical):
                return self.registry.get(canonical)
            raise ProviderNotFoundError(f"Requested provider '{requested_provider}' is not registered.")

        # 2. Check model routing in registry
        if model:
            by_model = self.registry.get_by_model(model)
            if by_model is not None:
                return by_model

            # Model prefix heuristic
            norm = model.strip().lower()
            spec = get_model_spec(norm)
            if spec.provider and self.registry.contains(spec.provider):
                return self.registry.get(spec.provider)

        # 3. Filter by capability if specified
        if capability:
            matches = self.registry.get_by_capability(capability)
            if matches:
                return matches[0]

        # 4. Default provider fallback
        if self.default_provider and self.registry.contains(self.default_provider):
            return self.registry.get(self.default_provider)

        # 5. Any registered provider
        names = self.registry.names()
        if names:
            return self.registry.get(names[0])

        raise ProviderNotFoundError("No suitable AI providers registered.")

    def generate(self, request: AIRequest) -> AIResponse:
        """
        Execute an inference request through middleware, retries, and provider routing.
        """
        provider = self.select_provider(
            model=request.model,
            requested_provider=request.provider,
            capability=ModelCapability.TEXT.value,
        )

        model_name = request.model or provider.default_model or "unknown"
        self._publish(AIRequestStarted(model=model_name, provider=provider.name))

        def terminal_call(req: AIRequest) -> AIResponse:
            start = time.perf_counter()
            try:
                # Prepare failover list starting with selected provider
                other_providers = [
                    self.registry.get(p)
                    for p in self.registry.names()
                    if p != provider.name
                ]
                chain = FailoverChain(
                    providers=[provider] + other_providers,
                    retry_policy=self.retry_policy,
                )

                response, active_provider = chain.execute(lambda p: p.generate(req))

                if active_provider.name != provider.name:
                    self._publish(
                        AIProviderChanged(
                            previous_provider=provider.name,
                            new_provider=active_provider.name,
                            reason="Failover triggered after primary provider error",
                        )
                    )

                latency_ms = (time.perf_counter() - start) * 1000.0
                self._publish(
                    AIRequestCompleted(
                        model=response.model,
                        provider=active_provider.name,
                        tokens=response.total_tokens,
                        latency_ms=latency_ms,
                    )
                )
                return response
            except Exception as e:
                err_msg = str(e)
                self._publish(
                    AIRequestFailed(
                        model=model_name,
                        provider=provider.name,
                        error=err_msg,
                    )
                )
                self.metrics.record_request(
                    latency_ms=(time.perf_counter() - start) * 1000.0,
                    success=False,
                )
                if isinstance(e, AIRequestTimeoutError):
                    if e.timeout is None:
                        e.timeout = req.timeout
                    raise
                elif isinstance(e, TimeoutError):
                    raise AIRequestTimeoutError(
                        message=f"AI request timed out: {err_msg}",
                        provider_name=provider.name,
                        timeout=req.timeout,
                    ) from e
                raise

        return self.pipeline.execute(request, terminal_call)

    def stream(self, request: AIRequest) -> StreamingIterator:
        """
        Initiate token streaming through the selected provider.
        """
        provider = self.select_provider(
            model=request.model,
            requested_provider=request.provider,
            capability=ModelCapability.STREAMING.value,
        )

        model_name = request.model or provider.default_model or "unknown"
        self._publish(AIStreamStarted(model=model_name, provider=provider.name))

        stream_iter = provider.stream(request)

        # Wrap iterator to emit completion event
        def wrap_stream():
            try:
                for chunk in stream_iter:
                    yield chunk
                self._publish(
                    AIStreamCompleted(
                        model=model_name,
                        provider=provider.name,
                        total_tokens=stream_iter.to_response().total_tokens,
                    )
                )
            except Exception as e:
                err_msg = str(e)
                self._publish(
                    AIRequestFailed(
                        model=model_name,
                        provider=provider.name,
                        error=err_msg,
                    )
                )
                if isinstance(e, AIRequestTimeoutError):
                    if e.timeout is None:
                        e.timeout = request.timeout
                    raise
                elif isinstance(e, TimeoutError):
                    raise AIRequestTimeoutError(
                        message=f"AI stream timed out: {err_msg}",
                        provider_name=provider.name,
                        timeout=request.timeout,
                    ) from e
                raise

        return StreamingIterator(
            generator=wrap_stream,
            model=model_name,
            provider=provider.name,
        )

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Generate vector embeddings through an embedding-capable provider.
        """
        provider = self.select_provider(
            model=request.model,
            capability=ModelCapability.EMBEDDINGS.value,
        )

        chain = FailoverChain(providers=[provider], retry_policy=self.retry_policy)
        result, _ = chain.execute(lambda p: p.embed(request))
        return result

    def create_session(
        self,
        model: str | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AISession:
        """Create a new stateful multi-turn AISession."""
        from scholaros.ai.session import AISession

        return AISession(
            manager=self,
            model=model,
            system_prompt=system_prompt,
            **kwargs,
        )

    def health(self, provider_name: str | None = None) -> ServiceHealth:
        """Check the health of a specific provider or the default provider."""
        target = provider_name or self.default_provider
        if not target:
            return ServiceHealth(
                service_name="AIManager",
                status=HealthStatus.UNKNOWN,
                details="No providers configured",
            )
        prov = self.registry.get(target)
        return prov.health()

    def health_all(self) -> dict[str, ServiceHealth]:
        """Check health across all registered providers."""
        reports: dict[str, ServiceHealth] = {}
        for name in self.registry.names():
            prov = self.registry.get(name)
            reports[name] = prov.health()
        return reports

    def switch_provider(self, new_default: str) -> None:
        """
        Switch the default provider and emit an AIProviderChanged event.
        """
        canonical = new_default.strip().lower()
        if not self.registry.contains(canonical):
            raise ProviderNotFoundError(f"Cannot switch to unregistered provider '{new_default}'.")
        old_provider = self.default_provider or "unknown"
        self.default_provider = canonical
        self._publish(
            AIProviderChanged(
                previous_provider=old_provider,
                new_provider=canonical,
                reason="Explicit provider switch",
            )
        )

    def list_models(
        self,
        capability: str | ModelCapability | None = None,
        provider: str | None = None,
        tier: ModelTier | None = None,
    ) -> list[ModelSpec]:
        """
        List known models filtered by capability, provider, and/or tier.
        """
        results: list[ModelSpec] = []
        cap_val = capability.value if isinstance(capability, ModelCapability) else capability

        for spec in KNOWN_MODELS.values():
            if provider and spec.provider != provider.strip().lower():
                continue
            if tier and spec.tier != tier:
                continue
            if cap_val and not spec.supports(cap_val):
                continue
            results.append(spec)

        return results

    def get_model(self, model_name: str) -> ModelSpec:
        """
        Retrieve specification for a given model.
        """
        return get_model_spec(model_name)

    def get_available_providers(self) -> list[str]:
        """
        Return the names of all registered providers.
        """
        return list(self.registry.names())

    def create_llm(
        self,
        model: str | None = None,
        provider: str | None = None,
        timeout: float | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLM:
        """
        Create a unified LLM instance backed by this manager's routing, retries, and middleware.
        """
        from scholaros.ai.llm.provider_adapter import ProviderLLM

        prov_inst = self.registry.get(provider) if provider else None
        return ProviderLLM(
            provider=prov_inst,
            manager=self,
            model=model,
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _publish(self, event: Event) -> None:
        """Publish lifecycle events to the EventBus if present."""
        if self.event_bus is not None:
            try:
                self.event_bus.publish(event)
            except Exception:
                pass


__all__ = [
    "AIEvent",
    "AIManager",
    "AIProviderChanged",
    "AIRequestCompleted",
    "AIRequestFailed",
    "AIRequestStarted",
    "AIStreamCompleted",
    "AIStreamStarted",
]
