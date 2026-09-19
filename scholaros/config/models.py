"""
ScholarOS Configuration Models (Compatibility Alias).

Re-exports typed models from scholaros.config.model.
"""

from __future__ import annotations

from scholaros.config.model import (
    AIConfig,
    AppConfig,
    GUIConfig,
    KnowledgeConfig,
    LLMConfig,
    LoggingConfig,
    ModelsConfig,
    PathsConfig,
    PluginsConfig,
    RAGConfig,
    RetrievalConfig,
    ServerConfig,
    StorageConfig,
)

__all__ = [
    "AIConfig",
    "AppConfig",
    "GUIConfig",
    "KnowledgeConfig",
    "LLMConfig",
    "LoggingConfig",
    "ModelsConfig",
    "PathsConfig",
    "PluginsConfig",
    "RAGConfig",
    "RetrievalConfig",
    "ServerConfig",
    "StorageConfig",
]
