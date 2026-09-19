"""
ScholarOS: A modular, multi-agent AI research operating system.

Public API surface frozen for V1.0.0.
"""

from __future__ import annotations

from scholaros.agents.researcher import ResearchAgent
from scholaros.ai.factory import AIFactory
from scholaros.container.container import Container
from scholaros.events.bus import EventBus
from scholaros.gui.application import GUIApplication
from scholaros.kernel.kernel import Kernel
from scholaros.knowledge.manager import KnowledgeManager
from scholaros.knowledge.rag.pipeline import RAGPipeline
from scholaros.plugins.base import Plugin
from scholaros.retrieval.hybrid import HybridRetriever

__version__ = "1.0.0"

__all__ = [
    "AIFactory",
    "Container",
    "EventBus",
    "GUIApplication",
    "HybridRetriever",
    "Kernel",
    "KnowledgeManager",
    "Plugin",
    "RAGPipeline",
    "ResearchAgent",
    "__version__",
]
