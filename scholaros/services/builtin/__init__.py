"""
ScholarOS Built-in Services Package.

Provides standard system and domain services for the ScholarOS ecosystem:
- AIService
- ToolService
- SchedulerService
- ResearchService
- KnowledgeService
- LoggingService
- MemoryService
- IndexingService
- CollaborationService
- PluginService
"""

from __future__ import annotations

from scholaros.services.builtin.ai import AIService
from scholaros.services.builtin.collaboration import CollaborationService
from scholaros.services.builtin.indexing import IndexingService
from scholaros.services.builtin.knowledge import KnowledgeService
from scholaros.services.builtin.logging import LoggingService
from scholaros.services.builtin.memory import MemoryService
from scholaros.services.builtin.plugin import PluginService
from scholaros.services.builtin.research import ResearchService
from scholaros.services.builtin.scheduler import SchedulerService
from scholaros.services.builtin.tool import ToolService

# Built-in Service Identifier Constants
AI_SERVICE = "AIService"
TOOL_SERVICE = "ToolService"
SCHEDULER_SERVICE = "SchedulerService"
RESEARCH_SERVICE = "ResearchService"
KNOWLEDGE_SERVICE = "KnowledgeService"
LOGGING_SERVICE = "LoggingService"
MEMORY_SERVICE = "MemoryService"
INDEXING_SERVICE = "IndexingService"
COLLABORATION_SERVICE = "CollaborationService"
PLUGIN_SERVICE = "PluginService"

__all__ = [
    # Constants
    "AI_SERVICE",
    "COLLABORATION_SERVICE",
    "INDEXING_SERVICE",
    "KNOWLEDGE_SERVICE",
    "LOGGING_SERVICE",
    "MEMORY_SERVICE",
    "PLUGIN_SERVICE",
    "RESEARCH_SERVICE",
    "SCHEDULER_SERVICE",
    "TOOL_SERVICE",
    # Service Classes
    "AIService",
    "CollaborationService",
    "IndexingService",
    "KnowledgeService",
    "LoggingService",
    "MemoryService",
    "PluginService",
    "ResearchService",
    "SchedulerService",
    "ToolService",
]
