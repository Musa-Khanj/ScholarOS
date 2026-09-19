"""
ScholarOS Configuration Models.

Typed data models defining the configuration schema for all core subsystems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scholaros.config.defaults import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_AI_BASE_URL,
    DEFAULT_AI_MAX_TOKENS,
    DEFAULT_AI_PROVIDER,
    DEFAULT_AI_TEMPERATURE,
    DEFAULT_AI_TIMEOUT,
    DEFAULT_AUTO_INDEX,
    DEFAULT_CACHE_PATH,
    DEFAULT_CHAT_MODEL,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CONTEXT_TOKEN_BUDGET,
    DEFAULT_DATA_PATH,
    DEFAULT_DEBUG,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_ENVIRONMENT,
    DEFAULT_GUI_FONT_FAMILY,
    DEFAULT_GUI_FONT_SIZE,
    DEFAULT_GUI_SIDEBAR_WIDTH,
    DEFAULT_GUI_THEME,
    DEFAULT_GUI_WINDOW_HEIGHT,
    DEFAULT_GUI_WINDOW_WIDTH,
    DEFAULT_KEYWORD_WEIGHT,
    DEFAULT_LLM_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_LOG_BACKUP_COUNT,
    DEFAULT_LOG_CONSOLE,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_MAX_BYTES,
    DEFAULT_PLUGINS_AUTO_LOAD,
    DEFAULT_PLUGINS_SANDBOX,
    DEFAULT_RAG_LIMIT,
    DEFAULT_RAG_MAX_TOKENS,
    DEFAULT_RAG_MIN_SCORE,
    DEFAULT_RAG_STRATEGY,
    DEFAULT_RAG_TIMEOUT,
    DEFAULT_RERANKER,
    DEFAULT_RESEARCH_MODEL,
    DEFAULT_RETRIEVAL_LIMIT,
    DEFAULT_RETRIEVAL_MIN_SCORE,
    DEFAULT_RETRIEVAL_STRATEGY,
    DEFAULT_RRF_K,
    DEFAULT_SEMANTIC_WEIGHT,
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    DEFAULT_STORAGE_BACKEND,
    DEFAULT_SUPPORTED_FORMATS,
    DEFAULT_TEMP_PATH,
    DEFAULT_WORKSPACE_PATH,
)
from scholaros.config.exceptions import ConfigurationError
from scholaros.config.security import mask_secret


@dataclass(slots=True)
class PathsConfig:
    workspace: Path = field(default_factory=lambda: DEFAULT_WORKSPACE_PATH)
    cache: Path = field(default_factory=lambda: DEFAULT_CACHE_PATH)
    data: Path = field(default_factory=lambda: DEFAULT_DATA_PATH)
    temp: Path = field(default_factory=lambda: DEFAULT_TEMP_PATH)

    def validate(self) -> None:
        """Validate paths configuration."""
        # Paths are always valid as Path objects

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
class StorageConfig:
    workspace: Path = field(default_factory=lambda: DEFAULT_WORKSPACE_PATH)
    cache: Path = field(default_factory=lambda: DEFAULT_CACHE_PATH)
    data: Path = field(default_factory=lambda: DEFAULT_DATA_PATH)
    temp: Path = field(default_factory=lambda: DEFAULT_TEMP_PATH)

    def validate(self) -> None:
        """Validate storage configuration."""
        # Storage paths are always valid as Path objects

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StorageConfig:
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
    file_path: Path | None = None
    console_output: bool = DEFAULT_LOG_CONSOLE
    max_bytes: int = DEFAULT_LOG_MAX_BYTES
    backup_count: int = DEFAULT_LOG_BACKUP_COUNT

    VALID_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

    def validate(self) -> None:
        """Validate logging configuration."""
        if self.level.upper() not in self.VALID_LEVELS:
            raise ConfigurationError(
                f"Invalid logging level '{self.level}'. Must be one of {sorted(self.VALID_LEVELS)}"
            )
        if self.max_bytes <= 0:
            raise ConfigurationError(f"max_bytes must be positive, got {self.max_bytes}")
        if self.backup_count < 0:
            raise ConfigurationError(f"backup_count must be non-negative, got {self.backup_count}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoggingConfig:
        file_val = data.get("file_path")
        return cls(
            level=str(data.get("level", DEFAULT_LOG_LEVEL)),
            format=str(data.get("format", DEFAULT_LOG_FORMAT)),
            file_path=Path(file_val) if file_val else None,
            console_output=bool(data.get("console_output", DEFAULT_LOG_CONSOLE)),
            max_bytes=int(data.get("max_bytes", DEFAULT_LOG_MAX_BYTES)),
            backup_count=int(data.get("backup_count", DEFAULT_LOG_BACKUP_COUNT)),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "level": self.level,
            "format": self.format,
            "console_output": self.console_output,
            "max_bytes": self.max_bytes,
            "backup_count": self.backup_count,
        }
        if self.file_path is not None:
            result["file_path"] = str(self.file_path)
        return result


@dataclass(slots=True)
class LLMConfig:
    provider: str = DEFAULT_LLM_PROVIDER
    model: str = DEFAULT_LLM_MODEL
    base_url: str = DEFAULT_LLM_BASE_URL
    temperature: float = DEFAULT_LLM_TEMPERATURE
    api_key: str | None = None
    timeout: float = 60.0

    def validate(self) -> None:
        """Validate LLM configuration."""
        if not self.provider.strip():
            raise ConfigurationError("LLM provider cannot be empty")
        if self.timeout <= 0:
            raise ConfigurationError(f"LLM timeout must be positive, got {self.timeout}")
        if self.temperature < 0.0:
            raise ConfigurationError(f"LLM temperature must be non-negative, got {self.temperature}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LLMConfig:
        return cls(
            provider=str(data.get("provider", DEFAULT_LLM_PROVIDER)),
            model=str(data.get("model", DEFAULT_LLM_MODEL)),
            base_url=str(data.get("base_url", DEFAULT_LLM_BASE_URL)),
            temperature=float(data.get("temperature", DEFAULT_LLM_TEMPERATURE)),
            api_key=data.get("api_key"),
            timeout=float(data.get("timeout", 60.0)),
        )

    def to_dict(self, mask_secrets: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "timeout": self.timeout,
        }
        if self.api_key is not None:
            result["api_key"] = mask_secret(self.api_key) if mask_secrets else self.api_key
        return result

    def __repr__(self) -> str:
        masked_key = mask_secret(self.api_key) if self.api_key else None
        return (
            f"LLMConfig(provider={self.provider!r}, model={self.model!r}, "
            f"base_url={self.base_url!r}, api_key={masked_key!r})"
        )


@dataclass(slots=True)
class AIConfig:
    provider: str = DEFAULT_AI_PROVIDER
    base_url: str = DEFAULT_AI_BASE_URL
    temperature: float = DEFAULT_AI_TEMPERATURE
    timeout: float = DEFAULT_AI_TIMEOUT
    max_tokens: int = DEFAULT_AI_MAX_TOKENS
    api_key: str | None = None
    providers: dict[str, dict[str, Any]] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate AI configuration."""
        if not self.provider.strip():
            raise ConfigurationError("AI provider cannot be empty")
        if self.timeout <= 0:
            raise ConfigurationError(f"AI timeout must be positive, got {self.timeout}")
        if self.max_tokens <= 0:
            raise ConfigurationError(f"AI max_tokens must be positive, got {self.max_tokens}")
        if self.temperature < 0.0:
            raise ConfigurationError(f"AI temperature must be non-negative, got {self.temperature}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AIConfig:
        providers_data = data.get("providers", {})
        return cls(
            provider=str(data.get("provider", DEFAULT_AI_PROVIDER)),
            base_url=str(data.get("base_url", DEFAULT_AI_BASE_URL)),
            temperature=float(data.get("temperature", DEFAULT_AI_TEMPERATURE)),
            timeout=float(data.get("timeout", DEFAULT_AI_TIMEOUT)),
            max_tokens=int(data.get("max_tokens", DEFAULT_AI_MAX_TOKENS)),
            api_key=data.get("api_key"),
            providers=dict(providers_data) if isinstance(providers_data, dict) else {},
        )

    def to_dict(self, mask_secrets: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {
            "provider": self.provider,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "max_tokens": self.max_tokens,
            "providers": dict(self.providers),
        }
        if self.api_key is not None:
            result["api_key"] = mask_secret(self.api_key) if mask_secrets else self.api_key
        if mask_secrets and self.providers:
            masked_providers: dict[str, dict[str, Any]] = {}
            for p_name, p_cfg in self.providers.items():
                masked_p = dict(p_cfg)
                if "api_key" in masked_p and masked_p["api_key"]:
                    masked_p["api_key"] = mask_secret(str(masked_p["api_key"]))
                masked_providers[p_name] = masked_p
            result["providers"] = masked_providers
        return result

    def __repr__(self) -> str:
        masked_key = mask_secret(self.api_key) if self.api_key else None
        return (
            f"AIConfig(provider={self.provider!r}, base_url={self.base_url!r}, "
            f"timeout={self.timeout}, api_key={masked_key!r})"
        )


@dataclass(slots=True)
class ModelsConfig:
    default_chat_model: str = DEFAULT_CHAT_MODEL
    default_research_model: str = DEFAULT_RESEARCH_MODEL
    default_embedding_model: str = DEFAULT_EMBEDDING_MODEL
    fallback_model: str | None = None

    def validate(self) -> None:
        """Validate models configuration."""
        if not self.default_chat_model.strip():
            raise ConfigurationError("default_chat_model cannot be empty")
        if not self.default_research_model.strip():
            raise ConfigurationError("default_research_model cannot be empty")
        if not self.default_embedding_model.strip():
            raise ConfigurationError("default_embedding_model cannot be empty")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelsConfig:
        return cls(
            default_chat_model=str(data.get("default_chat_model", DEFAULT_CHAT_MODEL)),
            default_research_model=str(data.get("default_research_model", DEFAULT_RESEARCH_MODEL)),
            default_embedding_model=str(data.get("default_embedding_model", DEFAULT_EMBEDDING_MODEL)),
            fallback_model=data.get("fallback_model"),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "default_chat_model": self.default_chat_model,
            "default_research_model": self.default_research_model,
            "default_embedding_model": self.default_embedding_model,
        }
        if self.fallback_model is not None:
            result["fallback_model"] = self.fallback_model
        return result


@dataclass(slots=True)
class RAGConfig:
    default_strategy: str = DEFAULT_RAG_STRATEGY
    default_limit: int = DEFAULT_RAG_LIMIT
    default_min_score: float = DEFAULT_RAG_MIN_SCORE
    default_max_tokens: int = DEFAULT_RAG_MAX_TOKENS
    system_prompt: str | None = None
    fallback_on_empty: bool = False
    timeout_seconds: float = DEFAULT_RAG_TIMEOUT
    enable_metrics: bool = True
    enable_events: bool = True

    def validate(self) -> None:
        """Validate RAG configuration."""
        if self.default_limit <= 0:
            raise ConfigurationError(f"RAG default_limit must be > 0, got {self.default_limit}")
        if self.default_max_tokens <= 0:
            raise ConfigurationError(f"RAG default_max_tokens must be > 0, got {self.default_max_tokens}")
        if self.default_min_score < 0.0:
            raise ConfigurationError(f"RAG default_min_score must be >= 0.0, got {self.default_min_score}")
        if self.timeout_seconds <= 0.0:
            raise ConfigurationError(f"RAG timeout_seconds must be > 0.0, got {self.timeout_seconds}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RAGConfig:
        return cls(
            default_strategy=str(data.get("default_strategy", DEFAULT_RAG_STRATEGY)),
            default_limit=int(data.get("default_limit", DEFAULT_RAG_LIMIT)),
            default_min_score=float(data.get("default_min_score", DEFAULT_RAG_MIN_SCORE)),
            default_max_tokens=int(data.get("default_max_tokens", DEFAULT_RAG_MAX_TOKENS)),
            system_prompt=data.get("system_prompt"),
            fallback_on_empty=bool(data.get("fallback_on_empty", False)),
            timeout_seconds=float(data.get("timeout_seconds", DEFAULT_RAG_TIMEOUT)),
            enable_metrics=bool(data.get("enable_metrics", True)),
            enable_events=bool(data.get("enable_events", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "default_strategy": self.default_strategy,
            "default_limit": self.default_limit,
            "default_min_score": self.default_min_score,
            "default_max_tokens": self.default_max_tokens,
            "fallback_on_empty": self.fallback_on_empty,
            "timeout_seconds": self.timeout_seconds,
            "enable_metrics": self.enable_metrics,
            "enable_events": self.enable_events,
        }
        if self.system_prompt is not None:
            result["system_prompt"] = self.system_prompt
        return result


@dataclass(slots=True)
class RetrievalConfig:
    default_strategy: str = DEFAULT_RETRIEVAL_STRATEGY
    default_limit: int = DEFAULT_RETRIEVAL_LIMIT
    min_score_threshold: float = DEFAULT_RETRIEVAL_MIN_SCORE
    semantic_weight: float = DEFAULT_SEMANTIC_WEIGHT
    keyword_weight: float = DEFAULT_KEYWORD_WEIGHT
    rrf_k: int = DEFAULT_RRF_K
    default_reranker: str = DEFAULT_RERANKER
    context_token_budget: int = DEFAULT_CONTEXT_TOKEN_BUDGET
    enable_metrics: bool = True
    enable_events: bool = True

    def validate(self) -> None:
        """Validate Retrieval configuration."""
        if self.default_limit <= 0:
            raise ConfigurationError(f"Retrieval default_limit must be > 0, got {self.default_limit}")
        if self.context_token_budget <= 0:
            raise ConfigurationError(f"context_token_budget must be > 0, got {self.context_token_budget}")
        if self.semantic_weight < 0.0 or self.keyword_weight < 0.0:
            raise ConfigurationError("Retrieval weights must be non-negative")
        if self.rrf_k <= 0:
            raise ConfigurationError(f"rrf_k must be > 0, got {self.rrf_k}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RetrievalConfig:
        return cls(
            default_strategy=str(data.get("default_strategy", DEFAULT_RETRIEVAL_STRATEGY)),
            default_limit=int(data.get("default_limit", DEFAULT_RETRIEVAL_LIMIT)),
            min_score_threshold=float(data.get("min_score_threshold", DEFAULT_RETRIEVAL_MIN_SCORE)),
            semantic_weight=float(data.get("semantic_weight", DEFAULT_SEMANTIC_WEIGHT)),
            keyword_weight=float(data.get("keyword_weight", DEFAULT_KEYWORD_WEIGHT)),
            rrf_k=int(data.get("rrf_k", DEFAULT_RRF_K)),
            default_reranker=str(data.get("default_reranker", DEFAULT_RERANKER)),
            context_token_budget=int(data.get("context_token_budget", DEFAULT_CONTEXT_TOKEN_BUDGET)),
            enable_metrics=bool(data.get("enable_metrics", True)),
            enable_events=bool(data.get("enable_events", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_strategy": self.default_strategy,
            "default_limit": self.default_limit,
            "min_score_threshold": self.min_score_threshold,
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight,
            "rrf_k": self.rrf_k,
            "default_reranker": self.default_reranker,
            "context_token_budget": self.context_token_budget,
            "enable_metrics": self.enable_metrics,
            "enable_events": self.enable_events,
        }


@dataclass(slots=True)
class KnowledgeConfig:
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    auto_index: bool = DEFAULT_AUTO_INDEX
    supported_formats: list[str] = field(default_factory=lambda: list(DEFAULT_SUPPORTED_FORMATS))
    storage_backend: str = DEFAULT_STORAGE_BACKEND

    def validate(self) -> None:
        """Validate knowledge configuration."""
        if self.chunk_size <= 0:
            raise ConfigurationError(f"chunk_size must be positive, got {self.chunk_size}")
        if self.chunk_overlap < 0:
            raise ConfigurationError(f"chunk_overlap must be non-negative, got {self.chunk_overlap}")
        if self.chunk_overlap >= self.chunk_size:
            raise ConfigurationError(
                f"chunk_overlap ({self.chunk_overlap}) must be smaller than chunk_size ({self.chunk_size})"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeConfig:
        formats = data.get("supported_formats", DEFAULT_SUPPORTED_FORMATS)
        return cls(
            chunk_size=int(data.get("chunk_size", DEFAULT_CHUNK_SIZE)),
            chunk_overlap=int(data.get("chunk_overlap", DEFAULT_CHUNK_OVERLAP)),
            auto_index=bool(data.get("auto_index", DEFAULT_AUTO_INDEX)),
            supported_formats=list(formats) if isinstance(formats, (list, tuple)) else list(DEFAULT_SUPPORTED_FORMATS),
            storage_backend=str(data.get("storage_backend", DEFAULT_STORAGE_BACKEND)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "auto_index": self.auto_index,
            "supported_formats": list(self.supported_formats),
            "storage_backend": self.storage_backend,
        }


@dataclass(slots=True)
class PluginsConfig:
    enabled_plugins: list[str] = field(default_factory=list)
    auto_load: bool = DEFAULT_PLUGINS_AUTO_LOAD
    plugin_directories: list[Path] = field(default_factory=lambda: [Path("plugins")])
    sandbox_enabled: bool = DEFAULT_PLUGINS_SANDBOX

    def validate(self) -> None:
        """Validate plugins configuration."""
        # Plugins configuration is valid

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PluginsConfig:
        dirs = data.get("plugin_directories", ["plugins"])
        dir_paths = [Path(d) for d in dirs] if isinstance(dirs, (list, tuple)) else [Path("plugins")]
        plugins = data.get("enabled_plugins", [])
        return cls(
            enabled_plugins=list(plugins) if isinstance(plugins, (list, tuple)) else [],
            auto_load=bool(data.get("auto_load", DEFAULT_PLUGINS_AUTO_LOAD)),
            plugin_directories=dir_paths,
            sandbox_enabled=bool(data.get("sandbox_enabled", DEFAULT_PLUGINS_SANDBOX)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled_plugins": list(self.enabled_plugins),
            "auto_load": self.auto_load,
            "plugin_directories": [str(p) for p in self.plugin_directories],
            "sandbox_enabled": self.sandbox_enabled,
        }


@dataclass(slots=True)
class GUIConfig:
    theme: str = DEFAULT_GUI_THEME
    window_width: int = DEFAULT_GUI_WINDOW_WIDTH
    window_height: int = DEFAULT_GUI_WINDOW_HEIGHT
    sidebar_width: int = DEFAULT_GUI_SIDEBAR_WIDTH
    font_family: str = DEFAULT_GUI_FONT_FAMILY
    font_size: int = DEFAULT_GUI_FONT_SIZE
    auto_save_state: bool = True

    def validate(self) -> None:
        """Validate GUI configuration."""
        if self.window_width <= 0:
            raise ConfigurationError(f"window_width must be positive, got {self.window_width}")
        if self.window_height <= 0:
            raise ConfigurationError(f"window_height must be positive, got {self.window_height}")
        if self.font_size <= 0:
            raise ConfigurationError(f"font_size must be positive, got {self.font_size}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GUIConfig:
        return cls(
            theme=str(data.get("theme", DEFAULT_GUI_THEME)),
            window_width=int(data.get("window_width", DEFAULT_GUI_WINDOW_WIDTH)),
            window_height=int(data.get("window_height", DEFAULT_GUI_WINDOW_HEIGHT)),
            sidebar_width=int(data.get("sidebar_width", DEFAULT_GUI_SIDEBAR_WIDTH)),
            font_family=str(data.get("font_family", DEFAULT_GUI_FONT_FAMILY)),
            font_size=int(data.get("font_size", DEFAULT_GUI_FONT_SIZE)),
            auto_save_state=bool(data.get("auto_save_state", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "window_width": self.window_width,
            "window_height": self.window_height,
            "sidebar_width": self.sidebar_width,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "auto_save_state": self.auto_save_state,
        }


@dataclass(slots=True)
class ServerConfig:
    host: str = DEFAULT_SERVER_HOST
    port: int = DEFAULT_SERVER_PORT

    def validate(self) -> None:
        """Validate server configuration."""
        if not (1 <= self.port <= 65535):
            raise ConfigurationError(f"Server port must be between 1 and 65535, got {self.port}")

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

    # Subsystem Configurations
    ai: AIConfig = field(default_factory=AIConfig)
    models: ModelsConfig = field(default_factory=ModelsConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    knowledge: KnowledgeConfig = field(default_factory=KnowledgeConfig)
    plugins: PluginsConfig = field(default_factory=PluginsConfig)
    gui: GUIConfig = field(default_factory=GUIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    server: ServerConfig = field(default_factory=ServerConfig)

    # Backward compatibility attributes
    paths: PathsConfig = field(default_factory=PathsConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)

    def __post_init__(self) -> None:
        # Keep legacy paths and storage aligned
        if self.storage and not self.paths:
            self.paths = PathsConfig(
                workspace=self.storage.workspace,
                cache=self.storage.cache,
                data=self.storage.data,
                temp=self.storage.temp,
            )

    def validate(self) -> None:
        """Validate the full application configuration tree."""
        self.ai.validate()
        self.models.validate()
        self.rag.validate()
        self.retrieval.validate()
        self.knowledge.validate()
        self.plugins.validate()
        self.gui.validate()
        self.logging.validate()
        self.storage.validate()
        self.server.validate()
        self.paths.validate()
        self.llm.validate()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppConfig:
        paths_data = data.get("paths") or data.get("storage") or {}
        storage_data = data.get("storage") or data.get("paths") or {}
        logging_data = data.get("logging", {})
        llm_data = data.get("llm") or data.get("ai") or {}
        ai_data = data.get("ai") or data.get("llm") or {}
        models_data = data.get("models", {})
        rag_data = data.get("rag", {})
        retrieval_data = data.get("retrieval", {})
        knowledge_data = data.get("knowledge", {})
        plugins_data = data.get("plugins", {})
        gui_data = data.get("gui", {})
        server_data = data.get("server", {})

        # If models wasn't populated but llm has model
        if not models_data and isinstance(llm_data, dict) and "model" in llm_data:
            models_data = {
                "default_chat_model": llm_data["model"],
                "default_research_model": llm_data["model"],
            }

        return cls(
            app_name=str(data.get("app_name", APP_NAME)),
            version=str(data.get("version", APP_VERSION)),
            environment=str(data.get("environment", DEFAULT_ENVIRONMENT)),
            debug=bool(data.get("debug", DEFAULT_DEBUG)),
            ai=AIConfig.from_dict(ai_data) if isinstance(ai_data, dict) else AIConfig(),
            models=ModelsConfig.from_dict(models_data) if isinstance(models_data, dict) else ModelsConfig(),
            rag=RAGConfig.from_dict(rag_data) if isinstance(rag_data, dict) else RAGConfig(),
            retrieval=RetrievalConfig.from_dict(retrieval_data) if isinstance(retrieval_data, dict) else RetrievalConfig(),
            knowledge=KnowledgeConfig.from_dict(knowledge_data) if isinstance(knowledge_data, dict) else KnowledgeConfig(),
            plugins=PluginsConfig.from_dict(plugins_data) if isinstance(plugins_data, dict) else PluginsConfig(),
            gui=GUIConfig.from_dict(gui_data) if isinstance(gui_data, dict) else GUIConfig(),
            logging=LoggingConfig.from_dict(logging_data) if isinstance(logging_data, dict) else LoggingConfig(),
            storage=StorageConfig.from_dict(storage_data) if isinstance(storage_data, dict) else StorageConfig(),
            server=ServerConfig.from_dict(server_data) if isinstance(server_data, dict) else ServerConfig(),
            paths=PathsConfig.from_dict(paths_data) if isinstance(paths_data, dict) else PathsConfig(),
            llm=LLMConfig.from_dict(llm_data) if isinstance(llm_data, dict) else LLMConfig(),
        )

    def to_dict(self, mask_secrets: bool = False) -> dict[str, Any]:
        """Convert entire configuration tree to dictionary with optional secret masking."""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "environment": self.environment,
            "debug": self.debug,
            "paths": self.paths.to_dict(),
            "storage": self.storage.to_dict(),
            "logging": self.logging.to_dict(),
            "llm": self.llm.to_dict(mask_secrets=mask_secrets),
            "ai": self.ai.to_dict(mask_secrets=mask_secrets),
            "models": self.models.to_dict(),
            "rag": self.rag.to_dict(),
            "retrieval": self.retrieval.to_dict(),
            "knowledge": self.knowledge.to_dict(),
            "plugins": self.plugins.to_dict(),
            "gui": self.gui.to_dict(),
            "server": self.server.to_dict(),
        }
