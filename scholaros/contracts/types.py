from __future__ import annotations

from enum import Enum


class ComponentType(str, Enum):
    AGENT = "agent"
    TOOL = "tool"
    PLUGIN = "plugin"
    MEMORY = "memory"
    LLM = "llm"
    VISION = "vision"
    RAG = "rag"


class EventPriority(int, Enum):
    LOW = 10
    NORMAL = 20
    HIGH = 30
    CRITICAL = 40