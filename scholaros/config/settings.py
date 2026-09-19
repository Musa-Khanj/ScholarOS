"""
ScholarOS Runtime Settings.

Provides an immutable snapshot of configuration for runtime use.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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


@dataclass(slots=True, frozen=True)
class Settings:
    """
    Immutable runtime settings container across all subsystems.
    """

    app_name: str
    version: str
    environment: str
    debug: bool

    # Subsystem settings
    ai: AIConfig
    models: ModelsConfig
    rag: RAGConfig
    retrieval: RetrievalConfig
    knowledge: KnowledgeConfig
    plugins: PluginsConfig
    gui: GUIConfig
    logging: LoggingConfig
    storage: StorageConfig
    server: ServerConfig

    # Legacy compatibility fields
    paths: PathsConfig
    llm: LLMConfig

    _raw: dict[str, Any]

    @classmethod
    def from_config(cls, config: AppConfig) -> Settings:
        """Create an immutable Settings object from an AppConfig."""
        return cls(
            app_name=config.app_name,
            version=config.version,
            environment=config.environment,
            debug=config.debug,
            ai=config.ai,
            models=config.models,
            rag=config.rag,
            retrieval=config.retrieval,
            knowledge=config.knowledge,
            plugins=config.plugins,
            gui=config.gui,
            logging=config.logging,
            storage=config.storage,
            server=config.server,
            paths=config.paths,
            llm=config.llm,
            _raw=config.to_dict(mask_secrets=False),
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

    def to_dict(self, mask_secrets: bool = False) -> dict[str, Any]:
        """Return dictionary representation, with optional secret masking."""
        if not mask_secrets:
            return dict(self._raw)
        # Deep mask using AppConfig
        return AppConfig.from_dict(self._raw).to_dict(mask_secrets=True)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"app_name={self.app_name!r}, "
            f"version={self.version!r}, "
            f"env={self.environment!r}, "
            f"debug={self.debug})"
        )
