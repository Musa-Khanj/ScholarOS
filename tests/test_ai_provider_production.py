"""
Milestone 10J — AI Provider & Model Production Completion Tests.

Validates:
- Multi-provider abstraction and provider switching
- Model discovery and capability routing
- Failover chain and retry behavior
- Timeout handling and AIRequestTimeoutError hierarchy
- ProviderLLM adapter and MockLLM implementation
- Health check aggregation across providers
- DI container dynamic provider resolution via LLMConfig
"""

from __future__ import annotations

from typing import Any
import pytest

from scholaros.ai.exceptions import (
    AIError,
    AIRequestTimeoutError,
    ProviderError,
    ProviderNotFoundError,
)
from scholaros.ai.llm.base import LLM
from scholaros.ai.llm.message import Message as LLMMessage, MessageRole as LLMMessageRole
from scholaros.ai.llm.mock import MockLLM
from scholaros.ai.llm.ollama import OllamaLLM
from scholaros.ai.llm.openai import OpenAILLM
from scholaros.ai.llm.anthropic import AnthropicLLM
from scholaros.ai.llm.provider_adapter import ProviderLLM
from scholaros.ai.manager import AIManager, AIProviderChanged
from scholaros.ai.models import ModelCapability, ModelTier
from scholaros.ai.provider import AIProvider
from scholaros.ai.providers.mock import MockProvider
from scholaros.ai.providers.registration import register_ai_services
from scholaros.ai.request import AIRequest
from scholaros.ai.response import AIResponse
from scholaros.ai.retry import RetryPolicy
from scholaros.config.model import LLMConfig
from scholaros.container import Container
from scholaros.events.bus import EventBus
from scholaros.events.event import Event
from scholaros.services.health import HealthStatus, ServiceHealth


class FailingProvider(AIProvider):
    """Provider that raises an error on generate for testing failover/retries."""

    def __init__(self, name: str = "failing", error_type: type[Exception] = ProviderError) -> None:
        super().__init__(name=name, capabilities={"text", "streaming"})
        self.error_type = error_type
        self.attempts: int = 0

    def generate(self, request: AIRequest) -> AIResponse:
        self.attempts += 1
        raise self.error_type(f"Simulated failure in {self.name}", provider_name=self.name)

    def stream(self, request: AIRequest) -> Any:
        raise self.error_type(f"Stream failure in {self.name}")

    def embed(self, request: Any) -> Any:
        raise self.error_type(f"Embed failure in {self.name}")

    def health(self) -> ServiceHealth:
        return ServiceHealth(service_name=self.name, status=HealthStatus.UNHEALTHY, details="Simulated down")


class TimingOutProvider(AIProvider):
    """Provider that raises TimeoutError for testing timeout handling."""

    def __init__(self, name: str = "timeout_prov") -> None:
        super().__init__(name=name, capabilities={"text", "streaming"})
        self.attempts: int = 0

    def generate(self, request: AIRequest) -> AIResponse:
        self.attempts += 1
        raise TimeoutError("Simulated socket read timeout")

    def stream(self, request: AIRequest) -> Any:
        raise TimeoutError("Simulated stream timeout")

    def embed(self, request: Any) -> Any:
        raise TimeoutError("Simulated embed timeout")

    def health(self) -> ServiceHealth:
        return ServiceHealth(service_name=self.name, status=HealthStatus.DEGRADED, details="High latency")


class TestAIProviderProduction:
    """Test suite for Milestone 10J AI provider independence."""

    def test_provider_registration_and_switching(self) -> None:
        """Test registering multiple providers and explicit provider switching with event emission."""
        events: list[Event] = []
        bus = EventBus()
        bus.subscribe("AIProviderChanged", lambda e: events.append(e))

        manager = AIManager(event_bus=bus)
        mock_p = MockProvider(name="mock_primary")
        mock_b = MockProvider(name="mock_backup")

        manager.register_provider(mock_p, default=True)
        manager.register_provider(mock_b)

        assert "mock_primary" in manager.get_available_providers()
        assert "mock_backup" in manager.get_available_providers()
        assert manager.default_provider == "mock_primary"

        # Switch default provider
        manager.switch_provider("mock_backup")
        assert manager.default_provider == "mock_backup"

        # Verify event was published
        assert len(events) == 1
        assert isinstance(events[0], AIProviderChanged)
        assert events[0].payload["previous_provider"] == "mock_primary"
        assert events[0].payload["new_provider"] == "mock_backup"

        # Switching to unregistered provider must raise ProviderNotFoundError
        with pytest.raises(ProviderNotFoundError):
            manager.switch_provider("non_existent_provider")

    def test_model_discovery_and_capability_routing(self) -> None:
        """Test list_models filtering by capability, provider, and tier."""
        manager = AIManager()

        # Filter by capability
        embedding_models = manager.list_models(capability=ModelCapability.EMBEDDINGS)
        assert len(embedding_models) >= 2
        assert all(m.supports(ModelCapability.EMBEDDINGS) for m in embedding_models)

        # Filter by provider
        openai_models = manager.list_models(provider="openai")
        assert len(openai_models) >= 2
        assert all(m.provider == "openai" for m in openai_models)

        # Filter by tier
        flagship_models = manager.list_models(tier=ModelTier.FLAGSHIP)
        assert len(flagship_models) >= 3
        assert all(m.tier == ModelTier.FLAGSHIP for m in flagship_models)

        # Model specification lookup
        spec = manager.get_model("gpt-4o")
        assert spec.name == "gpt-4o"
        assert spec.provider == "openai"
        assert spec.supports(ModelCapability.VISION)

        unknown_spec = manager.get_model("custom-finetuned-llama")
        assert unknown_spec.name == "custom-finetuned-llama"

    def test_failover_chain_execution(self) -> None:
        """Test multi-provider failover when the primary provider encounters errors."""
        events: list[Event] = []
        bus = EventBus()
        bus.subscribe("AIProviderChanged", lambda e: events.append(e))

        manager = AIManager(
            event_bus=bus,
            retry_policy=RetryPolicy(max_retries=1, initial_delay=0.01, jitter=False),
        )

        failing = FailingProvider(name="primary_failing")
        healthy = MockProvider(name="backup_healthy", default_response="Recovered from backup")

        manager.register_provider(failing, default=True)
        manager.register_provider(healthy)

        req = AIRequest.from_prompt("Explain quantum decoherence")
        resp = manager.generate(req)

        assert resp.content == "Recovered from backup"
        assert resp.provider == "backup_healthy"
        assert failing.attempts >= 1

        # Check provider change event
        prov_changed = [e for e in events if isinstance(e, AIProviderChanged)]
        assert len(prov_changed) == 1
        assert prov_changed[0].payload["previous_provider"] == "primary_failing"
        assert prov_changed[0].payload["new_provider"] == "backup_healthy"

    def test_timeout_error_handling_and_hierarchy(self) -> None:
        """Test AIRequestTimeoutError hierarchy and conversion of TimeoutError."""
        # Check hierarchy
        err = AIRequestTimeoutError("Gateway timeout", provider_name="slow_prov", timeout=30.0)
        assert isinstance(err, TimeoutError)
        assert isinstance(err, ProviderError)
        assert isinstance(err, AIError)
        assert err.provider_name == "slow_prov"
        assert err.timeout == 30.0

        # AIRequest timeout propagation
        req = AIRequest.from_prompt("Compute PI", timeout=15.5)
        assert req.timeout == 15.5
        req_copy = req.copy(temperature=0.2)
        assert req_copy.timeout == 15.5
        assert req_copy.temperature == 0.2

        # Provider timeout in AIManager
        manager = AIManager(
            retry_policy=RetryPolicy(max_retries=0),  # no retries to immediately catch
        )
        timing_out = TimingOutProvider("slow_service")
        manager.register_provider(timing_out, default=True)

        with pytest.raises(AIRequestTimeoutError) as exc_info:
            manager.generate(req)

        assert exc_info.value.provider_name == "slow_service"
        assert exc_info.value.timeout == 15.5
        assert isinstance(exc_info.value, TimeoutError)

    def test_mock_llm_features(self) -> None:
        """Test MockLLM canned responses, handlers, and call tracking."""
        # 1. Default response
        mock = MockLLM(default_response="Standard mock answer")
        assert mock.model == "mock-llm"
        r1 = mock.generate("Hello world")
        assert r1.content == "Standard mock answer"
        assert mock.call_count == 1

        # 2. Canned responses
        mock_canned = MockLLM(
            canned_responses={
                "quantum": "Quantum mechanics study atomic scales.",
                "relativity": "Einstein formulated general relativity.",
            }
        )
        r2 = mock_canned.generate([LLMMessage(role=LLMMessageRole.USER, content="Tell me about quantum physics")])
        assert r2.content == "Quantum mechanics study atomic scales."

        r3 = mock_canned.generate("Tell me about relativity")
        assert r3.content == "Einstein formulated general relativity."

        # 3. Custom handler
        mock_handler = MockLLM(handler=lambda msgs: f"Echo: {msgs}")
        r4 = mock_handler.generate("Test echo")
        assert r4.content == "Echo: Test echo"
        assert mock_handler.call_count == 1
        assert len(mock_handler.history) == 1

    def test_provider_llm_adapter_direct_and_manager(self) -> None:
        """Test ProviderLLM wrapping AIProvider and AIManager into LLM interface."""
        # Direct provider wrapping
        prov = MockProvider(name="mock_direct", default_response="Direct provider response")
        llm_direct = ProviderLLM(provider=prov, model="direct-model")
        assert llm_direct.model == "direct-model"

        resp1 = llm_direct.generate("What is 2+2?")
        assert resp1.content == "Direct provider response"
        assert resp1.model == "direct-model"
        assert prov.call_count == 1

        # Manager backed LLM
        mgr = AIManager()
        mgr_prov = MockProvider(name="manager_mock", default_response="Managed provider response")
        mgr.register_provider(mgr_prov, default=True)

        llm_managed = mgr.create_llm(model="managed-model")
        assert llm_managed.model == "managed-model"

        # Pass LLMMessage
        resp2 = llm_managed.generate([
            LLMMessage(role=LLMMessageRole.SYSTEM, content="You are a helpful assistant."),
            LLMMessage(role=LLMMessageRole.USER, content="Summarize RAG."),
        ])
        assert resp2.content == "Managed provider response"
        assert mgr_prov.call_count == 1

    def test_health_checks_aggregation(self) -> None:
        """Test health() and health_all() across multiple registered providers."""
        manager = AIManager()
        manager.register_provider(MockProvider(name="prov_healthy", healthy=True), default=True)
        manager.register_provider(FailingProvider(name="prov_failing"))
        manager.register_provider(TimingOutProvider(name="prov_degraded"))

        # Individual health check
        h_default = manager.health()
        assert h_default.status == HealthStatus.HEALTHY

        h_failing = manager.health("prov_failing")
        assert h_failing.status == HealthStatus.UNHEALTHY

        # Aggregated health check
        all_reports = manager.health_all()
        assert len(all_reports) == 3
        assert all_reports["prov_healthy"].status == HealthStatus.HEALTHY
        assert all_reports["prov_failing"].status == HealthStatus.UNHEALTHY
        assert all_reports["prov_degraded"].status == HealthStatus.DEGRADED

    def test_container_dynamic_provider_resolution(self) -> None:
        """Test DI container resolves LLM based on LLMConfig provider."""
        # 1. Default (no LLMConfig) -> OllamaLLM
        c1 = Container()
        register_ai_services(c1)
        llm1 = c1.resolve(LLM)
        assert isinstance(llm1, OllamaLLM)

        # 2. Configured for mock -> MockLLM
        c2 = Container()
        c2.add_instance(LLMConfig, LLMConfig(provider="mock", model="mock-test-model"))
        register_ai_services(c2)
        llm2 = c2.resolve(LLM)
        assert isinstance(llm2, MockLLM)
        assert llm2.model == "mock-test-model"

        # 3. Configured for openai -> OpenAILLM
        c3 = Container()
        c3.add_instance(LLMConfig, LLMConfig(provider="openai", model="gpt-4o-mini", api_key="sk-test-123"))
        register_ai_services(c3)
        llm3 = c3.resolve(LLM)
        assert isinstance(llm3, OpenAILLM)
        assert llm3.model == "gpt-4o-mini"

        # 4. Configured for anthropic -> AnthropicLLM
        c4 = Container()
        c4.add_instance(LLMConfig, LLMConfig(provider="anthropic", model="claude-3-haiku", api_key="ant-test-456"))
        register_ai_services(c4)
        llm4 = c4.resolve(LLM)
        assert isinstance(llm4, AnthropicLLM)
        assert llm4.model == "claude-3-haiku"

    def test_rag_and_research_agent_with_provider_llm(self) -> None:
        """Test that ProviderLLM seamlessly drives RAG pipeline and ResearchAgent."""
        from unittest.mock import Mock
        from scholaros.knowledge.rag.pipeline import RAGPipeline
        from scholaros.knowledge.rag.service import RAGService
        from scholaros.knowledge.rag.request import RAGRequest
        from scholaros.agents.researcher import ResearchAgent
        from scholaros.retrieval.pipeline import RetrievalPipeline
        from scholaros.retrieval.result import RetrievalResult

        mock_retrieval_pipe = Mock(spec=RetrievalPipeline)
        mock_retrieval_pipe.execute.return_value = (
            [
                RetrievalResult(
                    source="paper-transformer-01",
                    content="Transformers utilize multi-head self-attention mechanisms.",
                    score=0.95,
                    metadata={"topic": "deep learning"},
                )
            ],
            None,
        )

        mock_ai_prov = MockProvider(
            name="cloud_mock_ai",
            default_response="Transformers rely on multi-head self-attention.",
        )
        provider_llm = ProviderLLM(provider=mock_ai_prov, model="cloud-mock-model")

        rag_pipeline = RAGPipeline(
            retrieval_pipeline=mock_retrieval_pipe,
            llm=provider_llm,
        )
        rag_service = RAGService(pipeline=rag_pipeline)

        # 1. Test RAG execution
        rag_req = RAGRequest(query="How do transformers work?")
        rag_resp = rag_service.generate(rag_req)
        assert rag_resp.content == "Transformers rely on multi-head self-attention."
        assert "paper-transformer-01" in rag_resp.sources
        assert rag_resp.model == "cloud-mock-model"

        # 2. Test ResearchAgent execution with this RAGService
        agent = ResearchAgent.from_rag(rag_service)
        result = agent.research("Explain attention mechanisms")

        assert result.content == "Transformers rely on multi-head self-attention."
        assert "paper-transformer-01" in result.sources
        assert result.model == "cloud-mock-model"
