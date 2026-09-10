"""
ScholarOS Configuration Subsystem.
"""

from __future__ import annotations

from scholaros.config.defaults import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_CACHE_PATH,
    DEFAULT_DATA_PATH,
    DEFAULT_DEBUG,
    DEFAULT_ENVIRONMENT,
    DEFAULT_LLM_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    DEFAULT_TEMP_PATH,
    DEFAULT_WORKSPACE_PATH,
)
from scholaros.config.environment import (
    EnvironmentReader,
    get_env,
    load_environment,
)
from scholaros.config.exceptions import (
    ConfigurationError,
    ConfigurationLoadError,
    ConfigurationMissingError,
)
from scholaros.config.loader import ConfigLoader
from scholaros.config.manager import ConfigManager
from scholaros.config.model import (
    AppConfig,
    LLMConfig,
    LoggingConfig,
    PathsConfig,
    ServerConfig,
)
from scholaros.config.settings import Settings
from scholaros.config.sources import (
    CliSource,
    ConfigSource,
    ConfigurationSource,
    DefaultsSource,
    EnvironmentSource,
    FileSource,
)

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "AppConfig",
    "CliSource",
    "ConfigLoader",
    "ConfigManager",
    "ConfigSource",
    "ConfigurationError",
    "ConfigurationLoadError",
    "ConfigurationMissingError",
    "ConfigurationSource",
    "DEFAULT_CACHE_PATH",
    "DEFAULT_DATA_PATH",
    "DEFAULT_DEBUG",
    "DEFAULT_ENVIRONMENT",
    "DEFAULT_LLM_BASE_URL",
    "DEFAULT_LLM_MODEL",
    "DEFAULT_LLM_PROVIDER",
    "DEFAULT_LLM_TEMPERATURE",
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_SERVER_HOST",
    "DEFAULT_SERVER_PORT",
    "DEFAULT_TEMP_PATH",
    "DEFAULT_WORKSPACE_PATH",
    "DefaultsSource",
    "EnvironmentReader",
    "EnvironmentSource",
    "FileSource",
    "LLMConfig",
    "LoggingConfig",
    "PathsConfig",
    "ServerConfig",
    "Settings",
    "get_env",
    "load_environment",
]