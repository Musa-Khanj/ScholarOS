"""
Unit tests for ScholarOS RAG Configuration and Exceptions (Milestone 10E).
"""

from __future__ import annotations

import pytest

from scholaros.knowledge.exceptions import (
    KnowledgeError,
    RAGConfigurationError,
    RAGContextError,
    RAGError,
    RAGGenerationError,
    RAGPipelineError,
    RAGTimeoutError,
)
from scholaros.knowledge.rag.configuration import RAGConfiguration


class TestRAGExceptions:
    """Test RAG exception hierarchy and inheritance."""

    def test_rag_error_inheritance(self) -> None:
        err = RAGError("RAG failed")
        assert isinstance(err, KnowledgeError)
        assert isinstance(err, Exception)

    def test_pipeline_error_inheritance(self) -> None:
        err = RAGPipelineError("Pipeline step failed")
        assert isinstance(err, RAGError)
        assert isinstance(err, KnowledgeError)

    def test_specialized_exceptions(self) -> None:
        timeout_err = RAGTimeoutError("Timed out")
        assert isinstance(timeout_err, RAGPipelineError)

        gen_err = RAGGenerationError("LLM failed")
        assert isinstance(gen_err, RAGPipelineError)

        ctx_err = RAGContextError("Context packing failed")
        assert isinstance(ctx_err, RAGPipelineError)

        cfg_err = RAGConfigurationError("Invalid limit")
        assert isinstance(cfg_err, RAGError)


class TestRAGConfiguration:
    """Test RAGConfiguration defaults, validation, and dictionary conversion."""

    def test_default_configuration(self) -> None:
        cfg = RAGConfiguration()
        cfg.validate()

        assert cfg.default_strategy == "default"
        assert cfg.default_limit == 10
        assert cfg.default_min_score == 0.0
        assert cfg.default_max_tokens == 4000
        assert cfg.system_prompt is None
        assert cfg.fallback_on_empty is False
        assert cfg.empty_fallback_message is None
        assert cfg.enable_events is True
        assert cfg.enable_metrics is True
        assert cfg.timeout_seconds == 30.0
        assert cfg.extra_options == {}

    def test_validation_errors(self) -> None:
        with pytest.raises(RAGConfigurationError, match="default_limit must be > 0"):
            RAGConfiguration(default_limit=0).validate()

        with pytest.raises(RAGConfigurationError, match="default_max_tokens must be > 0"):
            RAGConfiguration(default_max_tokens=-1).validate()

        with pytest.raises(RAGConfigurationError, match="default_min_score must be >= 0.0"):
            RAGConfiguration(default_min_score=-0.5).validate()

        with pytest.raises(RAGConfigurationError, match="timeout_seconds must be > 0.0"):
            RAGConfiguration(timeout_seconds=0.0).validate()

    def test_to_and_from_dict(self) -> None:
        cfg = RAGConfiguration(
            default_strategy="hybrid",
            default_limit=5,
            default_min_score=0.25,
            default_max_tokens=2048,
            system_prompt="Custom prompt",
            fallback_on_empty=True,
            empty_fallback_message="Nothing found",
            enable_events=False,
            timeout_seconds=15.0,
            extra_options={"temperature": 0.7},
        )
        data = cfg.to_dict()
        assert data["default_strategy"] == "hybrid"
        assert data["default_limit"] == 5
        assert data["default_min_score"] == 0.25
        assert data["default_max_tokens"] == 2048
        assert data["system_prompt"] == "Custom prompt"
        assert data["fallback_on_empty"] is True
        assert data["empty_fallback_message"] == "Nothing found"
        assert data["enable_events"] is False
        assert data["timeout_seconds"] == 15.0
        assert data["extra_options"] == {"temperature": 0.7}

        restored = RAGConfiguration.from_dict(data)
        assert restored.default_strategy == "hybrid"
        assert restored.default_limit == 5
        assert restored.extra_options == {"temperature": 0.7}

    def test_from_dict_extra_keys(self) -> None:
        data = {
            "default_strategy": "semantic",
            "default_limit": 20,
            "custom_setting": 123,
        }
        cfg = RAGConfiguration.from_dict(data)
        assert cfg.default_strategy == "semantic"
        assert cfg.default_limit == 20
        assert cfg.extra_options.get("custom_setting") == 123
