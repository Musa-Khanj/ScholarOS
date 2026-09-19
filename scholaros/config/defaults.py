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

# Default Paths & Storage
DEFAULT_WORKSPACE_PATH: Path = Path("workspace")
DEFAULT_CACHE_PATH: Path = Path(".cache")
DEFAULT_DATA_PATH: Path = Path("data")
DEFAULT_TEMP_PATH: Path = Path(".temp")
DEFAULT_CONFIG_PATH: Path = Path("configs/default.toml")

# Default Logging
DEFAULT_LOG_LEVEL: str = "INFO"
DEFAULT_LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_LOG_CONSOLE: bool = True
DEFAULT_LOG_MAX_BYTES: int = 10485760
DEFAULT_LOG_BACKUP_COUNT: int = 5

# Default LLM / AI
DEFAULT_LLM_PROVIDER: str = "ollama"
DEFAULT_LLM_MODEL: str = "qwen2.5:1.5b"
DEFAULT_LLM_BASE_URL: str = "http://localhost:11434"
DEFAULT_LLM_TEMPERATURE: float = 0.0
DEFAULT_AI_PROVIDER: str = DEFAULT_LLM_PROVIDER
DEFAULT_AI_BASE_URL: str = DEFAULT_LLM_BASE_URL
DEFAULT_AI_TEMPERATURE: float = DEFAULT_LLM_TEMPERATURE
DEFAULT_AI_TIMEOUT: float = 60.0
DEFAULT_AI_MAX_TOKENS: int = 4096

# Default Models
DEFAULT_CHAT_MODEL: str = "qwen2.5:1.5b"
DEFAULT_RESEARCH_MODEL: str = "qwen2.5:1.5b"
DEFAULT_EMBEDDING_MODEL: str = "all-minilm:latest"

# Default RAG
DEFAULT_RAG_STRATEGY: str = "default"
DEFAULT_RAG_LIMIT: int = 10
DEFAULT_RAG_MIN_SCORE: float = 0.0
DEFAULT_RAG_MAX_TOKENS: int = 4000
DEFAULT_RAG_TIMEOUT: float = 30.0

# Default Retrieval
DEFAULT_RETRIEVAL_STRATEGY: str = "hybrid"
DEFAULT_RETRIEVAL_LIMIT: int = 10
DEFAULT_RETRIEVAL_MIN_SCORE: float = 0.0
DEFAULT_SEMANTIC_WEIGHT: float = 0.5
DEFAULT_KEYWORD_WEIGHT: float = 0.5
DEFAULT_RRF_K: int = 60
DEFAULT_RERANKER: str = "score"
DEFAULT_CONTEXT_TOKEN_BUDGET: int = 4000

# Default Knowledge
DEFAULT_CHUNK_SIZE: int = 1000
DEFAULT_CHUNK_OVERLAP: int = 200
DEFAULT_AUTO_INDEX: bool = True
DEFAULT_SUPPORTED_FORMATS: list[str] = ["txt", "md", "pdf"]
DEFAULT_STORAGE_BACKEND: str = "chroma"

# Default Plugins
DEFAULT_PLUGINS_AUTO_LOAD: bool = True
DEFAULT_PLUGINS_SANDBOX: bool = True

# Default GUI
DEFAULT_GUI_THEME: str = "system"
DEFAULT_GUI_WINDOW_WIDTH: int = 1200
DEFAULT_GUI_WINDOW_HEIGHT: int = 800
DEFAULT_GUI_SIDEBAR_WIDTH: int = 240
DEFAULT_GUI_FONT_FAMILY: str = "Segoe UI"
DEFAULT_GUI_FONT_SIZE: int = 10

# Default Server
DEFAULT_SERVER_HOST: str = "127.0.0.1"
DEFAULT_SERVER_PORT: int = 8000


def get_default_config_dict() -> dict[str, Any]:
    """
    Return the centralized default configuration as a nested dictionary.
    """
    storage_dict = {
        "workspace": str(DEFAULT_WORKSPACE_PATH),
        "cache": str(DEFAULT_CACHE_PATH),
        "data": str(DEFAULT_DATA_PATH),
        "temp": str(DEFAULT_TEMP_PATH),
    }

    logging_dict = {
        "level": DEFAULT_LOG_LEVEL,
        "format": DEFAULT_LOG_FORMAT,
        "console_output": DEFAULT_LOG_CONSOLE,
        "max_bytes": DEFAULT_LOG_MAX_BYTES,
        "backup_count": DEFAULT_LOG_BACKUP_COUNT,
    }

    ai_dict = {
        "provider": DEFAULT_AI_PROVIDER,
        "base_url": DEFAULT_AI_BASE_URL,
        "temperature": DEFAULT_AI_TEMPERATURE,
        "timeout": DEFAULT_AI_TIMEOUT,
        "max_tokens": DEFAULT_AI_MAX_TOKENS,
        "api_key": None,
        "providers": {},
    }

    models_dict = {
        "default_chat_model": DEFAULT_CHAT_MODEL,
        "default_research_model": DEFAULT_RESEARCH_MODEL,
        "default_embedding_model": DEFAULT_EMBEDDING_MODEL,
        "fallback_model": None,
    }

    rag_dict = {
        "default_strategy": DEFAULT_RAG_STRATEGY,
        "default_limit": DEFAULT_RAG_LIMIT,
        "default_min_score": DEFAULT_RAG_MIN_SCORE,
        "default_max_tokens": DEFAULT_RAG_MAX_TOKENS,
        "system_prompt": None,
        "fallback_on_empty": False,
        "timeout_seconds": DEFAULT_RAG_TIMEOUT,
        "enable_metrics": True,
        "enable_events": True,
    }

    retrieval_dict = {
        "default_strategy": DEFAULT_RETRIEVAL_STRATEGY,
        "default_limit": DEFAULT_RETRIEVAL_LIMIT,
        "min_score_threshold": DEFAULT_RETRIEVAL_MIN_SCORE,
        "semantic_weight": DEFAULT_SEMANTIC_WEIGHT,
        "keyword_weight": DEFAULT_KEYWORD_WEIGHT,
        "rrf_k": DEFAULT_RRF_K,
        "default_reranker": DEFAULT_RERANKER,
        "context_token_budget": DEFAULT_CONTEXT_TOKEN_BUDGET,
        "enable_metrics": True,
        "enable_events": True,
    }

    knowledge_dict = {
        "chunk_size": DEFAULT_CHUNK_SIZE,
        "chunk_overlap": DEFAULT_CHUNK_OVERLAP,
        "auto_index": DEFAULT_AUTO_INDEX,
        "supported_formats": list(DEFAULT_SUPPORTED_FORMATS),
        "storage_backend": DEFAULT_STORAGE_BACKEND,
    }

    plugins_dict = {
        "enabled_plugins": [],
        "auto_load": DEFAULT_PLUGINS_AUTO_LOAD,
        "plugin_directories": ["plugins"],
        "sandbox_enabled": DEFAULT_PLUGINS_SANDBOX,
    }

    gui_dict = {
        "theme": DEFAULT_GUI_THEME,
        "window_width": DEFAULT_GUI_WINDOW_WIDTH,
        "window_height": DEFAULT_GUI_WINDOW_HEIGHT,
        "sidebar_width": DEFAULT_GUI_SIDEBAR_WIDTH,
        "font_family": DEFAULT_GUI_FONT_FAMILY,
        "font_size": DEFAULT_GUI_FONT_SIZE,
        "auto_save_state": True,
    }

    server_dict = {
        "host": DEFAULT_SERVER_HOST,
        "port": DEFAULT_SERVER_PORT,
    }

    # Backward compatible LLM dict
    llm_dict = {
        "provider": DEFAULT_LLM_PROVIDER,
        "model": DEFAULT_LLM_MODEL,
        "base_url": DEFAULT_LLM_BASE_URL,
        "temperature": DEFAULT_LLM_TEMPERATURE,
        "timeout": DEFAULT_AI_TIMEOUT,
    }

    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": DEFAULT_ENVIRONMENT,
        "debug": DEFAULT_DEBUG,
        "paths": dict(storage_dict),
        "storage": storage_dict,
        "logging": logging_dict,
        "llm": llm_dict,
        "ai": ai_dict,
        "models": models_dict,
        "rag": rag_dict,
        "retrieval": retrieval_dict,
        "knowledge": knowledge_dict,
        "plugins": plugins_dict,
        "gui": gui_dict,
        "server": server_dict,
    }
