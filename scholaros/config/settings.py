"""
ScholarOS Runtime Settings.

Provides an immutable snapshot of configuration for runtime use.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scholaros.config.model import (
    AppConfig,
    LLMConfig,
    LoggingConfig,
    PathsConfig,
    ServerConfig,
)


@dataclass(slots=True, frozen=True)
class Settings:
    """
    Immutable runtime settings container.
    """

    app_name: str
    version: str
    environment: str
    debug: bool
    paths: PathsConfig
    logging: LoggingConfig
    llm: LLMConfig
    server: ServerConfig
    _raw: dict[str, Any]

    @classmethod
    def from_config(cls, config: AppConfig) -> Settings:
        """Create an immutable Settings object from an AppConfig."""
        return cls(
            app_name=config.app_name,
            version=config.version,
            environment=config.environment,
            debug=config.debug,
            paths=config.paths,
            logging=config.logging,
            llm=config.llm,
            server=config.server,
            _raw=config.to_dict(),
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Safely retrieve a configuration setting by name or dotted path."""
        if "." in key:
            parts = key.split(".")
            curr: Any = self._raw
            for part in parts:
                if isinstance(curr, dict) and part in curr:
                    curr = curr[part]
                else:
                    return default
            return curr
        return getattr(self, key, self._raw.get(key, default))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._raw)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"app_name={self.app_name!r}, "
            f"version={self.version!r}, "
            f"env={self.environment!r}, "
            f"debug={self.debug})"
        )
