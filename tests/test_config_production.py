"""
Production Integration and Verification Tests for ScholarOS Configuration Subsystem.

Milestone 10M: Configuration & Settings Completion.
Tests typed models across all 9 sections, defaults, validation, environment
variable parsing, secret masking, JSON/TOML persistence, and GUI SettingsView integration.
"""

from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
import tomllib
from unittest.mock import Mock
import pytest

from scholaros.config import (
    AIConfig,
    AppConfig,
    ConfigManager,
    ConfigurationError,
    EnvironmentReader,
    GUIConfig,
    KnowledgeConfig,
    LLMConfig,
    LoggingConfig,
    ModelsConfig,
    PluginsConfig,
    RAGConfig,
    RetrievalConfig,
    SecretStr,
    ServerConfig,
    StorageConfig,
    mask_secret,
)
from scholaros.gui.application import GUIApplication
from scholaros.gui.views.workspace_views import SettingsView


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

_root: tk.Tk | None = None


def get_test_root() -> tk.Tk:
    """Return a shared withdrawn Tk root instance for widget instantiation."""
    global _root
    if _root is None:
        default_root = getattr(tk, "_default_root", None)
        if default_root is not None:
            _root = default_root
        else:
            try:
                _root = tk.Tk()
                _root.withdraw()
            except Exception as e:
                pytest.skip(f"Tkinter unavailable: {e}")
    return _root


@pytest.fixture
def test_root():
    root = get_test_root()
    for child in list(root.winfo_children()):
        try:
            child.destroy()
        except Exception:
            pass
    return root


# ---------------------------------------------------------------------------
# 1. Subsystem Configuration Models & Validation
# ---------------------------------------------------------------------------

def test_subsystem_models_and_validation():
    # 1. AIConfig
    ai = AIConfig(provider="openai", base_url="https://api.openai.com/v1", api_key="sk-test12345678")
    ai.validate()
    assert ai.provider == "openai"
    assert repr(ai) != "sk-test12345678"  # Must mask secret in repr
    with pytest.raises(ConfigurationError):
        AIConfig(provider="", timeout=10.0).validate()
    with pytest.raises(ConfigurationError):
        AIConfig(timeout=-5.0).validate()

    # 2. ModelsConfig
    models = ModelsConfig(
        default_chat_model="gpt-4o",
        default_research_model="o3-mini",
        default_embedding_model="text-embedding-3-small",
    )
    models.validate()
    with pytest.raises(ConfigurationError):
        ModelsConfig(default_chat_model="").validate()

    # 3. RAGConfig
    rag = RAGConfig(default_strategy="hybrid", default_limit=5, default_min_score=0.2)
    rag.validate()
    with pytest.raises(ConfigurationError):
        RAGConfig(default_limit=0).validate()
    with pytest.raises(ConfigurationError):
        RAGConfig(default_max_tokens=-1).validate()

    # 4. RetrievalConfig
    retrieval = RetrievalConfig(default_strategy="hybrid", semantic_weight=0.7, keyword_weight=0.3)
    retrieval.validate()
    with pytest.raises(ConfigurationError):
        RetrievalConfig(semantic_weight=-0.1).validate()
    with pytest.raises(ConfigurationError):
        RetrievalConfig(rrf_k=0).validate()

    # 5. KnowledgeConfig
    knowledge = KnowledgeConfig(chunk_size=500, chunk_overlap=100)
    knowledge.validate()
    with pytest.raises(ConfigurationError):
        KnowledgeConfig(chunk_size=0).validate()
    with pytest.raises(ConfigurationError):
        KnowledgeConfig(chunk_size=500, chunk_overlap=600).validate()

    # 6. PluginsConfig
    plugins = PluginsConfig(enabled_plugins=["research-tool"], auto_load=True)
    plugins.validate()
    assert "research-tool" in plugins.enabled_plugins

    # 7. GUIConfig
    gui = GUIConfig(theme="dark", window_width=1400, window_height=900)
    gui.validate()
    with pytest.raises(ConfigurationError):
        GUIConfig(window_width=0).validate()

    # 8. LoggingConfig
    logging_cfg = LoggingConfig(level="DEBUG")
    logging_cfg.validate()
    with pytest.raises(ConfigurationError):
        LoggingConfig(level="INVALID_LEVEL").validate()

    # 9. StorageConfig
    storage = StorageConfig(workspace=Path("custom_ws"))
    storage.validate()
    assert storage.workspace == Path("custom_ws")

    # 10. ServerConfig
    server = ServerConfig(port=8080)
    server.validate()
    with pytest.raises(ConfigurationError):
        ServerConfig(port=70000).validate()


def test_app_config_full_tree_and_validation():
    app_cfg = AppConfig()
    app_cfg.validate()

    assert app_cfg.ai.provider == "ollama"
    assert app_cfg.models.default_chat_model == "qwen2.5:1.5b"
    assert app_cfg.rag.default_strategy == "default"
    assert app_cfg.retrieval.default_strategy == "hybrid"
    assert app_cfg.knowledge.chunk_size == 1000
    assert app_cfg.plugins.auto_load is True
    assert app_cfg.gui.theme == "system"
    assert app_cfg.logging.level == "INFO"
    assert app_cfg.storage.workspace == Path("workspace")

    # Legacy compatibility fields
    assert app_cfg.llm.provider == "ollama"
    assert app_cfg.paths.workspace == Path("workspace")


# ---------------------------------------------------------------------------
# 2. Security & Secret Handling
# ---------------------------------------------------------------------------

def test_secret_masking_and_secret_str():
    # Long secret
    secret = "sk-ant-api03-1234567890abcdef"
    masked = mask_secret(secret, visible_start=4, visible_end=4)
    assert masked.startswith("sk-a")
    assert masked.endswith("cdef")
    assert "***" in masked
    assert secret not in masked

    # Short secret
    short = "short"
    assert mask_secret(short) == "***"

    # Empty and None
    assert mask_secret("") == ""
    assert mask_secret(None) == ""

    # SecretStr class
    sec_str = SecretStr("super-secret-passphrase-123")
    assert sec_str.get_secret_value() == "super-secret-passphrase-123"
    assert "super-secret-passphrase-123" not in repr(sec_str)
    assert "super-secret-passphrase-123" not in str(sec_str)
    assert sec_str == "super-secret-passphrase-123"


def test_app_config_secret_masking():
    app_cfg = AppConfig(
        ai=AIConfig(
            provider="openai",
            api_key="sk-secret-token-abcdef123456",
            providers={
                "openai": {"api_key": "sk-secret-token-abcdef123456"},
            },
        ),
        llm=LLMConfig(api_key="sk-secret-token-abcdef123456"),
    )

    unmasked_dict = app_cfg.to_dict(mask_secrets=False)
    assert unmasked_dict["ai"]["api_key"] == "sk-secret-token-abcdef123456"
    assert unmasked_dict["llm"]["api_key"] == "sk-secret-token-abcdef123456"

    masked_dict = app_cfg.to_dict(mask_secrets=True)
    assert masked_dict["ai"]["api_key"] != "sk-secret-token-abcdef123456"
    assert "***" in masked_dict["ai"]["api_key"]
    assert masked_dict["llm"]["api_key"] != "sk-secret-token-abcdef123456"
    assert "***" in masked_dict["ai"]["providers"]["openai"]["api_key"]


# ---------------------------------------------------------------------------
# 3. Environment Variable Ingestion
# ---------------------------------------------------------------------------

def test_environment_configuration(monkeypatch):
    monkeypatch.setenv("SCHOLAROS_AI__PROVIDER", "anthropic")
    monkeypatch.setenv("SCHOLAROS_AI__API_KEY", "sk-ant-test-key-123")
    monkeypatch.setenv("SCHOLAROS_MODELS__DEFAULT_CHAT_MODEL", "claude-3-5-sonnet")
    monkeypatch.setenv("SCHOLAROS_RAG__DEFAULT_LIMIT", "15")
    monkeypatch.setenv("SCHOLAROS_KNOWLEDGE__CHUNK_SIZE", "800")
    monkeypatch.setenv("SCHOLAROS_GUI__THEME", "dark")
    monkeypatch.setenv("SCHOLAROS_STORAGE__WORKSPACE", "env_workspace")

    reader = EnvironmentReader()
    env_data = reader.load_prefixed()

    assert env_data["ai"]["provider"] == "anthropic"
    assert env_data["ai"]["api_key"] == "sk-ant-test-key-123"
    assert env_data["models"]["default_chat_model"] == "claude-3-5-sonnet"
    assert env_data["rag"]["default_limit"] == 15
    assert env_data["knowledge"]["chunk_size"] == 800
    assert env_data["gui"]["theme"] == "dark"
    assert env_data["storage"]["workspace"] == "env_workspace"

    # Ingest into AppConfig
    cfg = AppConfig.from_dict(env_data)
    assert cfg.ai.provider == "anthropic"
    assert cfg.models.default_chat_model == "claude-3-5-sonnet"
    assert cfg.rag.default_limit == 15
    assert cfg.knowledge.chunk_size == 800
    assert cfg.gui.theme == "dark"


def test_standard_third_party_env_keys(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-live-key-999")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-live-key-888")
    monkeypatch.setenv("OLLAMA_HOST", "http://remote-ollama:11434")

    reader = EnvironmentReader()
    data = reader.load_prefixed()

    assert data["ai"]["providers"]["openai"]["api_key"] == "sk-openai-live-key-999"
    assert data["ai"]["providers"]["anthropic"]["api_key"] == "sk-ant-live-key-888"
    assert data["ai"]["base_url"] == "http://remote-ollama:11434"


# ---------------------------------------------------------------------------
# 4. Persistence: JSON and TOML
# ---------------------------------------------------------------------------

def test_config_manager_persistence_json(tmp_path):
    mgr = ConfigManager()
    json_path = tmp_path / "test_config.json"

    # Save to JSON
    saved_path = mgr.save(json_path)
    assert saved_path.exists()

    # Load file and check structure
    with json_path.open("r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["app_name"] == "ScholarOS"
    assert loaded["ai"]["provider"] == "ollama"
    assert loaded["rag"]["default_strategy"] == "default"

    # Update config and persist
    mgr.update(
        {
            "ai": {"provider": "openai"},
            "rag": {"default_limit": 25},
        },
        persist=True,
        persist_path=json_path,
    )

    with json_path.open("r", encoding="utf-8") as f:
        reloaded = json.load(f)
    assert reloaded["ai"]["provider"] == "openai"
    assert reloaded["rag"]["default_limit"] == 25
    assert mgr.config.ai.provider == "openai"
    assert mgr.settings.ai.provider == "openai"


def test_config_manager_persistence_toml(tmp_path):
    mgr = ConfigManager()
    toml_path = tmp_path / "test_config.toml"

    # Save to TOML
    saved_path = mgr.save(toml_path, format="toml")
    assert saved_path.exists()

    # Verify TOML roundtrip with standard tomllib
    with toml_path.open("rb") as f:
        parsed_toml = tomllib.load(f)
    assert parsed_toml["app_name"] == "ScholarOS"
    assert parsed_toml["ai"]["provider"] == "ollama"
    assert parsed_toml["models"]["default_chat_model"] == "qwen2.5:1.5b"


# ---------------------------------------------------------------------------
# 5. GUI Application & SettingsView Integration
# ---------------------------------------------------------------------------

def test_gui_application_config_delegation(tmp_path):
    mock_window = Mock()
    mgr = ConfigManager()
    app = GUIApplication(window=mock_window, config_manager=mgr)

    assert app.config_manager is mgr
    config = app.get_config()
    assert config.app_name == "ScholarOS"

    settings = app.get_settings()
    assert settings.ai.provider == "ollama"

    # Dynamic update through GUIApplication
    save_file = tmp_path / "app_config.json"
    app.update_config({"ai": {"provider": "anthropic"}}, persist=True, persist_path=save_file)

    assert app.get_config().ai.provider == "anthropic"
    assert save_file.exists()


def test_settings_view_ui_integration(test_root):
    mock_app = Mock()
    config = AppConfig(
        ai=AIConfig(provider="ollama", base_url="http://localhost:11434", api_key="secret-key-1234"),
        models=ModelsConfig(default_chat_model="qwen2.5:1.5b", default_research_model="qwen2.5:1.5b"),
        rag=RAGConfig(default_strategy="hybrid", default_limit=12),
        storage=StorageConfig(workspace=Path("my_workspace")),
    )
    mock_app.get_config.return_value = config
    mock_app.info.return_value = {"status": "Running", "provider": "ollama"}

    view = SettingsView(test_root, application=mock_app)

    # Initial form state check
    assert view._provider_combo.get() == "ollama"
    assert view._base_url_entry.get() == "http://localhost:11434"
    assert view._api_key_entry.get() == "secret-key-1234"
    assert view._api_key_entry.cget("show") == "*"
    assert view._rag_limit_entry.get() == "12"
    assert view._workspace_entry.get() == "my_workspace"

    # Toggle API key visibility
    view._show_key_var.set(True)
    view.toggle_key_visibility()
    assert view._api_key_entry.cget("show") == ""
    view._show_key_var.set(False)
    view.toggle_key_visibility()
    assert view._api_key_entry.cget("show") == "*"

    # Modify form values and save
    view._provider_combo.set("openai")
    view._chat_model_entry.delete(0, "end")
    view._chat_model_entry.insert(0, "gpt-4o")
    view._rag_limit_entry.delete(0, "end")
    view._rag_limit_entry.insert(0, "20")

    saved_updates = view.save_settings()
    assert saved_updates is not None
    assert saved_updates["ai"]["provider"] == "openai"
    assert saved_updates["models"]["default_chat_model"] == "gpt-4o"
    assert saved_updates["rag"]["default_limit"] == 20
    mock_app.update_config.assert_called_once()
