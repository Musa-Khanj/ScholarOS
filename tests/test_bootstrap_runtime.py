"""
Tests for ScholarOS Bootstrap Runtime (Part 1 Composition Root).
"""

from __future__ import annotations

from unittest.mock import Mock

from scholaros.ai.manager import AIManager
from scholaros.bootstrap import Bootstrap, RuntimeServices, bootstrap_runtime
from scholaros.config.manager import ConfigManager
from scholaros.container.container import Container
from scholaros.events.bus import EventBus
from scholaros.gui.builder import GUIBuilder
from scholaros.gui.launcher import GUILauncher
from scholaros.knowledge.manager import KnowledgeManager
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.knowledge.rag.service import RAGService
from scholaros.plugins.manager import PluginManager
from scholaros.research.pipeline import ResearchPipeline
from scholaros.retrieval.pipeline import RetrievalPipeline
from scholaros.services.builtin.research import ResearchService
from scholaros.services.manager import ServiceManager


def test_bootstrap_runtime_creates_all_subsystems():
    """Verify bootstrap_runtime creates all required production subsystems."""
    runtime = bootstrap_runtime(use_mock_ai=True)

    assert isinstance(runtime, RuntimeServices)
    assert isinstance(runtime.container, Container)
    assert isinstance(runtime.config_manager, ConfigManager)
    assert isinstance(runtime.event_bus, EventBus)
    assert isinstance(runtime.ai_manager, AIManager)
    assert isinstance(runtime.knowledge_manager, KnowledgeManager)
    assert isinstance(runtime.retrieval_pipeline, RetrievalPipeline)
    assert isinstance(runtime.rag_pipeline, RAGPipeline)
    assert isinstance(runtime.rag_service, RAGService)
    assert isinstance(runtime.research_pipeline, ResearchPipeline)
    assert isinstance(runtime.research_service, ResearchService)
    assert isinstance(runtime.plugin_manager, PluginManager)
    assert isinstance(runtime.service_manager, ServiceManager)


def test_bootstrap_runtime_registers_instances_in_container():
    """Verify services can be resolved directly from DI container."""
    runtime = bootstrap_runtime(use_mock_ai=True)
    c = runtime.container

    assert c.resolve(ConfigManager) is runtime.config_manager
    assert c.resolve(EventBus) is runtime.event_bus
    assert c.resolve(AIManager) is runtime.ai_manager
    assert c.resolve(KnowledgeManager) is runtime.knowledge_manager
    assert c.resolve(RetrievalPipeline) is runtime.retrieval_pipeline
    assert c.resolve(RAGPipeline) is runtime.rag_pipeline
    assert c.resolve(RAGService) is runtime.rag_service
    assert c.resolve(ResearchPipeline) is runtime.research_pipeline
    assert c.resolve(PluginManager) is runtime.plugin_manager
    assert c.resolve(ServiceManager) is runtime.service_manager


def test_bootstrap_class_initialization():
    """Verify Bootstrap class wires runtime and lifecycle."""
    boot = Bootstrap(use_mock_ai=True)
    assert isinstance(boot.runtime, RuntimeServices)
    assert boot.container is boot.runtime.container
    assert boot.services is boot.runtime
    assert boot.configuration is boot.runtime.config


def test_gui_launcher_resolves_from_bootstrap_runtime():
    """Verify GUILauncher passes bootstrap runtime services to GUIBuilder."""
    mock_builder = Mock(spec=GUIBuilder)
    mock_integration = Mock()
    mock_builder.build.return_value = mock_integration

    launcher = GUILauncher(builder=mock_builder, use_mock_ai=True)
    launcher.launch()

    mock_builder.build.assert_called_once()
    call_kwargs = mock_builder.build.call_args.kwargs
    assert "services" in call_kwargs
    assert isinstance(call_kwargs["services"], RuntimeServices)
    assert "container" in call_kwargs
    assert isinstance(call_kwargs["container"], Container)
    mock_integration.run.assert_called_once()
