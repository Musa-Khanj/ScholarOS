"""
ScholarOS RAG Service.

Bridges the RAG subsystem with the ScholarOS Service Framework and
Dependency Injection Container.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.knowledge.rag.configuration import RAGConfiguration
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.request import RAGRequest
from scholaros.knowledge.rag.response import RAGResponse
from scholaros.services.health import ServiceHealth
from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service

if TYPE_CHECKING:
    from scholaros.ai.llm.base import LLM
    from scholaros.container.container import Container
    from scholaros.events.bus import EventBus
    from scholaros.retrieval.manager import RetrievalManager
    from scholaros.retrieval.pipeline import RetrievalPipeline


class RAGService(Service):
    """
    Service encapsulating ScholarOS Retrieval-Augmented Generation.
    """

    def __init__(
        self,
        pipeline: RAGPipeline | None = None,
        retrieval_pipeline: RetrievalPipeline | None = None,
        retrieval_manager: RetrievalManager | None = None,
        llm: LLM | None = None,
        config: RAGConfiguration | None = None,
        event_bus: EventBus | None = None,
        system_prompt: str | None = None,
        metadata: ServiceMetadata | None = None,
    ) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="RAGService",
                version="1.0.0",
                description="ScholarOS Retrieval-Augmented Generation Service",
                capabilities=("rag", "grounded_generation", "attribution", "diagnostics"),
                tags=("knowledge", "rag", "ai"),
            )
        super().__init__(metadata=metadata)

        self._config = config or RAGConfiguration()
        self._event_bus = event_bus

        if pipeline is not None:
            self._pipeline = pipeline
        elif retrieval_manager is not None and llm is not None:
            self._pipeline = RAGPipeline.from_manager(
                manager=retrieval_manager,
                llm=llm,
                strategy=self._config.default_strategy,
                system_prompt=system_prompt or self._config.system_prompt,
                fallback_on_empty=self._config.fallback_on_empty,
                empty_fallback_message=self._config.empty_fallback_message,
                event_bus=event_bus,
                config=self._config,
            )
        elif retrieval_pipeline is not None and llm is not None:
            self._pipeline = RAGPipeline(
                retrieval_pipeline=retrieval_pipeline,
                llm=llm,
                system_prompt=system_prompt or self._config.system_prompt,
                fallback_on_empty=self._config.fallback_on_empty,
                empty_fallback_message=self._config.empty_fallback_message,
                event_bus=event_bus,
                config=self._config,
            )
        else:
            raise ValueError(
                "RAGService requires either an existing RAGPipeline or (retrieval_pipeline/retrieval_manager and llm)."
            )

    @property
    def pipeline(self) -> RAGPipeline:
        """Return the underlying RAGPipeline."""
        return self._pipeline

    @property
    def config(self) -> RAGConfiguration:
        """Return the RAG configuration."""
        return self._config

    @property
    def event_bus(self) -> EventBus | None:
        """Return the attached EventBus, if configured."""
        return self._event_bus

    # ---------------------------------------------------------
    # Execution Operations
    # ---------------------------------------------------------

    def generate(self, request: RAGRequest | str) -> RAGResponse:
        """Execute RAG generation for a request or query string."""
        if isinstance(request, str):
            req = RAGRequest(
                query=request,
                strategy=self._config.default_strategy,
                limit=self._config.default_limit,
                minimum_score=self._config.default_min_score,
                max_tokens=self._config.default_max_tokens,
                fallback_on_empty=self._config.fallback_on_empty,
                empty_fallback_message=self._config.empty_fallback_message,
            )
        else:
            req = request
        return self._pipeline.execute(req)

    def ask(self, query: str, **kwargs: Any) -> str:
        """Convenience method to query RAG and return just the answer text."""
        limit = kwargs.get("limit", self._config.default_limit)
        strategy = kwargs.get("strategy", self._config.default_strategy)
        min_score = kwargs.get("min_score", self._config.default_min_score)
        max_tokens = kwargs.get("max_tokens", self._config.default_max_tokens)
        collections = kwargs.get("collections")

        req = RAGRequest(
            query=query,
            strategy=strategy,
            limit=limit,
            minimum_score=min_score,
            max_tokens=max_tokens,
            collections=collections,
            fallback_on_empty=self._config.fallback_on_empty,
            empty_fallback_message=self._config.empty_fallback_message,
        )
        response = self._pipeline.execute(req)
        return response.content

    # ---------------------------------------------------------
    # Health & Diagnostics
    # ---------------------------------------------------------

    def health(self) -> ServiceHealth:
        """Evaluate and return service health status."""
        from scholaros.services.health import HealthStatus

        healthy = (
            self._pipeline is not None
            and self._pipeline.llm is not None
            and self._pipeline.retrieval_pipeline is not None
        )
        status = HealthStatus.HEALTHY if healthy else HealthStatus.UNHEALTHY
        details_str = "RAG service operational" if healthy else "RAG service components missing or uninitialized"

        metrics_dict: dict[str, Any] = {
            "has_pipeline": self._pipeline is not None,
            "has_llm": self._pipeline.llm is not None,
            "has_retrieval": self._pipeline.retrieval_pipeline is not None,
            "fallback_on_empty": self._config.fallback_on_empty,
        }
        return ServiceHealth(
            service_name=self.name,
            status=status,
            details=details_str,
            metrics=metrics_dict,
        )

    # ---------------------------------------------------------
    # DI Container Integration
    # ---------------------------------------------------------

    def register_container(self, container: Container) -> None:
        """Register RAG components into the DI container."""
        container.add_instance(RAGService, self)
        container.add_instance(RAGPipeline, self._pipeline)
        container.add_instance(RAGConfiguration, self._config)

    @classmethod
    def configure_container(
        cls,
        container: Container,
        pipeline: RAGPipeline | None = None,
        retrieval_pipeline: RetrievalPipeline | None = None,
        retrieval_manager: RetrievalManager | None = None,
        llm: LLM | None = None,
        config: RAGConfiguration | None = None,
        event_bus: EventBus | None = None,
        system_prompt: str | None = None,
    ) -> RAGService:
        """Convenience factory to instantiate RAGService and register in Container."""
        service = cls(
            pipeline=pipeline,
            retrieval_pipeline=retrieval_pipeline,
            retrieval_manager=retrieval_manager,
            llm=llm,
            config=config,
            event_bus=event_bus,
            system_prompt=system_prompt,
        )
        service.register_container(container)
        return service

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"status={self.status.name}"
            f")"
        )


__all__ = [
    "RAGService",
]
