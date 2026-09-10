"""
ScholarOS Configuration Defaults.

Provides centralized default values for application configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

APP_NAME: str = "ScholarOS"
APP_VERSION: str = "1.0.0"
DEFAULT_ENVIRONMENT: str = "development"
DEFAULT_DEBUG: bool = False

# Default Paths
DEFAULT_WORKSPACE_PATH: Path = Path("workspace")
DEFAULT_CACHE_PATH: Path = Path(".cache")
DEFAULT_DATA_PATH: Path = Path("data")
DEFAULT_TEMP_PATH: Path = Path(".temp")
DEFAULT_CONFIG_PATH: Path = Path("configs/default.toml")

# Default Logging
DEFAULT_LOG_LEVEL: str = "INFO"
DEFAULT_LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Default LLM
DEFAULT_LLM_PROVIDER: str = "ollama"
DEFAULT_LLM_MODEL: str = "qwen2.5:1.5b"
DEFAULT_LLM_BASE_URL: str = "http://localhost:11434"
DEFAULT_LLM_TEMPERATURE: float = 0.0

# Default Server
DEFAULT_SERVER_HOST: str = "127.0.0.1"
DEFAULT_SERVER_PORT: int = 8000


def get_default_config_dict() -> dict[str, Any]:
    """
    Return the centralized default configuration as a dictionary.
    """
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": DEFAULT_ENVIRONMENT,
        "debug": DEFAULT_DEBUG,
        "paths": {
            "workspace": str(DEFAULT_WORKSPACE_PATH),
            "cache": str(DEFAULT_CACHE_PATH),
            "data": str(DEFAULT_DATA_PATH),
            "temp": str(DEFAULT_TEMP_PATH),
        },
        "logging": {
            "level": DEFAULT_LOG_LEVEL,
            "format": DEFAULT_LOG_FORMAT,
        },
        "llm": {
            "provider": DEFAULT_LLM_PROVIDER,
            "model": DEFAULT_LLM_MODEL,
            "base_url": DEFAULT_LLM_BASE_URL,
            "temperature": DEFAULT_LLM_TEMPERATURE,
        },
        "server": {
            "host": DEFAULT_SERVER_HOST,
            "port": DEFAULT_SERVER_PORT,
        },
    }
