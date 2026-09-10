"""
ScholarOS Configuration Models (Compatibility Alias).

Re-exports typed models from scholaros.config.model.
"""

from __future__ import annotations

from scholaros.config.model import (
    AppConfig,
    LLMConfig,
    LoggingConfig,
    PathsConfig,
    ServerConfig,
)

__all__ = [
    "AppConfig",
    "LLMConfig",
    "LoggingConfig",
    "PathsConfig",
    "ServerConfig",
]