"""
ScholarOS Bootstrap Runtime (Composition Root).

Constructs and wires the complete production runtime object graph:
Platform -> Configuration -> EventBus -> Container -> AI -> Knowledge -> Retrieval -> RAG -> Research -> Plugins -> Services.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scholaros.ai.factory import AIFactory
from scholaros.ai.llm.provider_adapter import ProviderLLM
from scholaros.ai.manager import AIManager
from scholaros.ai.providers.mock import MockProvider
from scholaros.ai.providers.ollama import OllamaProvider
from scholaros.ai.registry import ProviderRegistry
from scholaros.config.manager import ConfigManager
from scholaros.config.model import AppConfig
from scholaros.container.container import Container
from scholaros.embeddings.in_memory_vector_store import InMemoryVectorStore
from scholaros.events.bus import EventBus
from scholaros.knowledge.manager import KnowledgeManager
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.service import RAGService
from scholaros.platform.paths import initialize_user_environment
from scholaros.plugins.manager import PluginManager
from scholaros.research.pipeline import ResearchPipeline
from scholaros.retrieval.cache import RetrievalCache
from scholaros.retrieval.hybrid import HybridRetriever
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.services.builtin.ai import AIService
from scholaros.services.builtin.knowledge import KnowledgeService
from scholaros.services.builtin.plugin import PluginService
from scholaros.services.builtin.research import ResearchService
from scholaros.services.manager import ServiceManager
from scholaros.services.provider import configure_services


@dataclass
class RuntimeServices:
    """
    Bundles the fully wired production runtime subsystems.
    """

    container: Container
    config_manager: ConfigManager
    config: AppConfig
    event_bus: EventBus
    ai_manager: AIManager
    knowledge_manager: KnowledgeManager
    retrieval_pipeline: RetrievalPipeline
    rag_pipeline: RAGPipeline
    rag_service: RAGService
    research_pipeline: ResearchPipeline
    research_service: ResearchService
    plugin_manager: PluginManager
    service_manager: ServiceManager

    def get_service(self, service_type: type[Any]) -> Any:
        """Resolve a service from the underlying container."""
        return self.container.resolve(service_type)


def bootstrap_runtime(
    config_path: Path | str | None = None,
    overrides: dict[str, Any] | None = None,
    use_mock_ai: bool = False,
) -> RuntimeServices:
    """
    Authoritative ScholarOS Composition Root.

    Constructs and registers all core subsystems, services, managers,
    and pipelines into a unified dependency injection container and
    returns a structured RuntimeServices bundle.
    """
    # 1. Platform User Environment
    initialize_user_environment()

    # 2. Configuration Manager
    config_manager = ConfigManager()
    if config_path is not None:
        config_manager.load(config_path, **(overrides or {}))
    elif overrides:
        config_manager.load(**overrides)

    config = config_manager.config

    # 3. Event Bus & DI Container
    event_bus = EventBus()
    container = Container()

    # 4. AI Subsystem & Providers
    registry = ProviderRegistry()
    ai_manager = AIManager(
        registry=registry,
        event_bus=event_bus,
    )

    # Always register MockProvider for offline fallback and deterministic testing
    mock_prov = MockProvider(
        name="mock",
        default_response="ScholarOS V1 Research & Knowledge Core is operational.",
        dimensions=384,
    )
    ai_manager.register_provider(mock_prov)

    # Register Ollama Provider from config
    ollama_base_url = "http://localhost:11434"
    ollama_model = "qwen2.5:1.5b"
    if hasattr(config, "ai") and getattr(config.ai, "base_url", None):
        ollama_base_url = config.ai.base_url
    if hasattr(config, "models") and getattr(config.models, "default_chat_model", None):
        ollama_model = config.models.default_chat_model

    try:
        ollama_prov = OllamaProvider(
            base_url=ollama_base_url,
            default_model=ollama_model,
        )
        ai_manager.register_provider(ollama_prov)
    except Exception:
        pass

    # Optional cloud providers if keys are configured
    if hasattr(config, "ai") and getattr(config.ai, "api_key", None):
        api_key = config.ai.api_key
        prov_name = getattr(config.ai, "provider", "").lower()
        if prov_name in ("openai", "anthropic", "google", "openrouter"):
            try:
                cloud_prov = AIFactory.create_provider(prov_name, api_key=api_key)
                ai_manager.register_provider(cloud_prov)
            except Exception:
                pass

    if use_mock_ai:
        ai_manager.switch_provider("mock")
    elif hasattr(config, "ai") and config.ai.provider in ai_manager.get_available_providers():
        ai_manager.switch_provider(config.ai.provider)
    elif "ollama" in ai_manager.get_available_providers():
        ai_manager.switch_provider("ollama")
    else:
        ai_manager.switch_provider("mock")

    # 5. Knowledge Subsystem
    active_ai_provider = ai_manager.select_provider()
    vector_store = InMemoryVectorStore()
    knowledge_manager = KnowledgeManager(
        event_bus=event_bus,
        ai_provider=active_ai_provider,
        vector_store=vector_store,
    )

    # 6. Retrieval Pipeline
    retrieval_cache = RetrievalCache(max_size=200, default_ttl=3600.0)
    retriever = HybridRetriever(
        vector_store=vector_store,
        ai_provider=active_ai_provider,
        storage=knowledge_manager.storage,
    )
    retrieval_pipeline = RetrievalPipeline(
        retriever=retriever,
        cache=retrieval_cache,
    )

    # 7. Grounded RAG Pipeline & Service
    llm_adapter = ProviderLLM(manager=ai_manager)
    rag_pipeline = RAGPipeline(
        retrieval_pipeline=retrieval_pipeline,
        llm=llm_adapter,
    )
    rag_service = RAGService(pipeline=rag_pipeline)

    # 8. Research Pipeline & Service
    research_pipeline = ResearchPipeline(
        rag=rag_pipeline,
        event_bus=event_bus,
    )
    research_service = ResearchService(pipeline=research_pipeline)

    # 9. Plugin Manager
    plugin_manager = PluginManager(
        container=container,
        event_bus=event_bus,
        config=config,
    )
    try:
        plugin_manager.discover()
    except Exception:
        pass

    # 10. Service Manager & Built-in Services
    service_manager = ServiceManager(
        event_bus=event_bus,
        container=container,
    )

    # Register built-ins into ServiceManager
    try:
        service_manager.register(AIService())
        service_manager.register(KnowledgeService())
        service_manager.register(PluginService())
        service_manager.register(research_service)
    except Exception:
        pass

    # Bind ServiceManager into container
    configure_services(container, service_manager)

    # 11. Register all subsystems into DI Container
    container.add_instance(ConfigManager, config_manager)
    container.add_instance(EventBus, event_bus)
    container.add_instance(AIManager, ai_manager)
    container.add_instance(KnowledgeManager, knowledge_manager)
    container.add_instance(RetrievalPipeline, retrieval_pipeline)
    container.add_instance(RAGPipeline, rag_pipeline)
    container.add_instance(RAGService, rag_service)
    container.add_instance(ResearchPipeline, research_pipeline)
    container.add_instance(PluginManager, plugin_manager)
    # Note: ServiceManager and ResearchService are registered into container by configure_services()

    return RuntimeServices(
        container=container,
        config_manager=config_manager,
        config=config,
        event_bus=event_bus,
        ai_manager=ai_manager,
        knowledge_manager=knowledge_manager,
        retrieval_pipeline=retrieval_pipeline,
        rag_pipeline=rag_pipeline,
        rag_service=rag_service,
        research_pipeline=research_pipeline,
        research_service=research_service,
        plugin_manager=plugin_manager,
        service_manager=service_manager,
    )
