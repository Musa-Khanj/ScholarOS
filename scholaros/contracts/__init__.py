"""
ScholarOS Contracts and System Interfaces.
"""

from __future__ import annotations

from scholaros.contracts.component import (
    Component,
    ComponentMetadata,
    ComponentStatus,
)
from scholaros.contracts.exceptions import (
    AgentError,
    ConfigurationError,
    LLMError,
    MemoryError,
    PluginError,
    RAGError,
    RegistryError,
    ScholarOSError,
    ToolError,
    VisionError,
)
from scholaros.contracts.retrieval import (
    ContextBuilderProtocol,
    FilterProtocol,
    HybridRetrieverContract,
    PipelineProtocol,
    RerankerProtocol,
    RetrieverProtocol,
    StrategyProtocol,
    VectorRetrieverContract,
)
from scholaros.contracts.types import (
    ComponentType,
    EventPriority,
)

__all__ = [
    # Components & Lifecycles
    "Component",
    "ComponentMetadata",
    "ComponentStatus",
    "ComponentType",
    "EventPriority",
    # Exceptions
    "ScholarOSError",
    "ConfigurationError",
    "PluginError",
    "ToolError",
    "AgentError",
    "RegistryError",
    "MemoryError",
    "VisionError",
    "LLMError",
    "RAGError",
    # Retrieval Contracts
    "RetrieverProtocol",
    "RerankerProtocol",
    "FilterProtocol",
    "PipelineProtocol",
    "ContextBuilderProtocol",
    "StrategyProtocol",
    "VectorRetrieverContract",
    "HybridRetrieverContract",
]
