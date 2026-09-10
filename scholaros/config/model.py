"""
ScholarOS Configuration Models.

Typed data models defining the configuration schema.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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


@dataclass(slots=True)
class PathsConfig:
    workspace: Path = field(default_factory=lambda: DEFAULT_WORKSPACE_PATH)
    cache: Path = field(default_factory=lambda: DEFAULT_CACHE_PATH)
    data: Path = field(default_factory=lambda: DEFAULT_DATA_PATH)
    temp: Path = field(default_factory=lambda: DEFAULT_TEMP_PATH)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PathsConfig:
        return cls(
            workspace=Path(data.get("workspace", DEFAULT_WORKSPACE_PATH)),
            cache=Path(data.get("cache", DEFAULT_CACHE_PATH)),
            data=Path(data.get("data", DEFAULT_DATA_PATH)),
            temp=Path(data.get("temp", DEFAULT_TEMP_PATH)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace": str(self.workspace),
            "cache": str(self.cache),
            "data": str(self.data),
            "temp": str(self.temp),
        }


@dataclass(slots=True)
class LoggingConfig:
    level: str = DEFAULT_LOG_LEVEL
    format: str = DEFAULT_LOG_FORMAT

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoggingConfig:
        return cls(
            level=str(data.get("level", DEFAULT_LOG_LEVEL)),
            format=str(data.get("format", DEFAULT_LOG_FORMAT)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "format": self.format,
        }


@dataclass(slots=True)
class LLMConfig:
    provider: str = DEFAULT_LLM_PROVIDER
    model: str = DEFAULT_LLM_MODEL
    base_url: str = DEFAULT_LLM_BASE_URL
    temperature: float = DEFAULT_LLM_TEMPERATURE

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LLMConfig:
        return cls(
            provider=str(data.get("provider", DEFAULT_LLM_PROVIDER)),
            model=str(data.get("model", DEFAULT_LLM_MODEL)),
            base_url=str(data.get("base_url", DEFAULT_LLM_BASE_URL)),
            temperature=float(data.get("temperature", DEFAULT_LLM_TEMPERATURE)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
        }


@dataclass(slots=True)
class ServerConfig:
    host: str = DEFAULT_SERVER_HOST
    port: int = DEFAULT_SERVER_PORT

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ServerConfig:
        return cls(
            host=str(data.get("host", DEFAULT_SERVER_HOST)),
            port=int(data.get("port", DEFAULT_SERVER_PORT)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
        }


@dataclass(slots=True)
class AppConfig:
    app_name: str = APP_NAME
    version: str = APP_VERSION
    environment: str = DEFAULT_ENVIRONMENT
    debug: bool = DEFAULT_DEBUG

    paths: PathsConfig = field(default_factory=PathsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    server: ServerConfig = field(default_factory=ServerConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppConfig:
        paths_data = data.get("paths", {})
        logging_data = data.get("logging", {})
        llm_data = data.get("llm", {})
        server_data = data.get("server", {})

        return cls(
            app_name=str(data.get("app_name", APP_NAME)),
            version=str(data.get("version", APP_VERSION)),
            environment=str(data.get("environment", DEFAULT_ENVIRONMENT)),
            debug=bool(data.get("debug", DEFAULT_DEBUG)),
            paths=PathsConfig.from_dict(paths_data) if isinstance(paths_data, dict) else PathsConfig(),
            logging=LoggingConfig.from_dict(logging_data) if isinstance(logging_data, dict) else LoggingConfig(),
            llm=LLMConfig.from_dict(llm_data) if isinstance(llm_data, dict) else LLMConfig(),
            server=ServerConfig.from_dict(server_data) if isinstance(server_data, dict) else ServerConfig(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "version": self.version,
            "environment": self.environment,
            "debug": self.debug,
            "paths": self.paths.to_dict(),
            "logging": self.logging.to_dict(),
            "llm": self.llm.to_dict(),
            "server": self.server.to_dict(),
        }
