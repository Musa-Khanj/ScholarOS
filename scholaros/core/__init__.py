"""
ScholarOS Core Package
"""

from __future__ import annotations

from scholaros.core.base import (
    Component,
    ComponentMetadata,
    ComponentStatus,
)
from scholaros.core.commands import (
    Command,
    CommandBus,
    CommandHandler,
)
from scholaros.core.container import ServiceContainer
from scholaros.core.event import (
    Event,
    EventBus,
    EventCallback,
)
from scholaros.core.exceptions import (
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
from scholaros.core.registry import Registry
from scholaros.core.types import (
    ComponentType,
    EventPriority,
)

__all__ = [
    "AgentError",
    "Command",
    "CommandBus",
    "CommandHandler",
    "Component",
    "ComponentMetadata",
    "ComponentStatus",
    "ComponentType",
    "ConfigurationError",
    "Event",
    "EventBus",
    "EventCallback",
    "EventPriority",
    "LLMError",
    "MemoryError",
    "PluginError",
    "RAGError",
    "Registry",
    "RegistryError",
    "ScholarOSError",
    "ServiceContainer",
    "ToolError",
    "VisionError",
]
