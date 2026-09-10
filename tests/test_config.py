from __future__ import annotations

import json
import os
from pathlib import Path
import pytest

from scholaros.config import (
    APP_NAME,
    APP_VERSION,
    AppConfig,
    CliSource,
    ConfigLoader,
    ConfigManager,
    ConfigSource,
    ConfigurationError,
    ConfigurationLoadError,
    ConfigurationMissingError,
    DefaultsSource,
    EnvironmentReader,
    EnvironmentSource,
    FileSource,
    LLMConfig,
    LoggingConfig,
    PathsConfig,
    ServerConfig,
    Settings,
    get_env,
    load_environment,
)
from scholaros.config.defaults import get_default_config_dict


# ---------------------------------------------------------------------------
# 1. Existing Test Compatibility
# ---------------------------------------------------------------------------

def test_default_config():
    manager = ConfigManager()
    manager.load(Path("configs/default.toml"))
    assert manager.config.app_name == "ScholarOS"


# ---------------------------------------------------------------------------
# 2. Defaults Tests
# ---------------------------------------------------------------------------

def test_defaults_constants():
    assert APP_NAME == "ScholarOS"
    assert APP_VERSION == "1.0.0"
    defaults = get_default_config_dict()
    assert defaults["app_name"] == "ScholarOS"
    assert "paths" in defaults
    assert "logging" in defaults
    assert "llm" in defaults
    assert "server" in defaults


# ---------------------------------------------------------------------------
# 3. Environment Tests
# ---------------------------------------------------------------------------

def test_environment_reader(monkeypatch):
    monkeypatch.setenv("SCHOLAROS_APP_NAME", "EnvScholar")
    monkeypatch.setenv("SCHOLAROS_DEBUG", "true")
    monkeypatch.setenv("SCHOLAROS_LOGGING_LEVEL", "DEBUG")
    monkeypatch.setenv("SCHOLAROS_SERVER_PORT", "9000")

    reader = EnvironmentReader(prefix="SCHOLAROS_")
    assert reader.prefix == "SCHOLAROS_"
    assert reader.get_str("SCHOLAROS_APP_NAME") == "EnvScholar"
    assert reader.get_bool("SCHOLAROS_DEBUG") is True
    assert reader.get_int("SCHOLAROS_SERVER_PORT") == 9000
    assert reader.get_float("SCHOLAROS_NONEXISTENT", 1.5) == 1.5
    assert reader.get_path("SCHOLAROS_NONEXISTENT", Path("fallback")) == Path("fallback")

    prefixed = reader.load_prefixed()
    assert prefixed["app_name"] == "EnvScholar"
    assert prefixed["debug"] is True
    assert prefixed["logging"]["level"] == "DEBUG"
    assert prefixed["server"]["port"] == 9000

    # Module-level convenience functions
    assert get_env("SCHOLAROS_APP_NAME") == "EnvScholar"
    env_dict = load_environment(prefix="SCHOLAROS_")
    assert env_dict["app_name"] == "EnvScholar"


# ---------------------------------------------------------------------------
# 4. Model Tests
# ---------------------------------------------------------------------------

def test_config_models():
    paths = PathsConfig(
        workspace=Path("ws"),
        cache=Path("c"),
        data=Path("d"),
        temp=Path("t"),
    )
    assert paths.to_dict()["workspace"] == "ws"
    recreated_paths = PathsConfig.from_dict(paths.to_dict())
    assert recreated_paths.workspace == Path("ws")

    logging_cfg = LoggingConfig(level="WARNING", format="%(message)s")
    assert logging_cfg.to_dict()["level"] == "WARNING"

    llm_cfg = LLMConfig(provider="anthropic", model="claude-3-5-sonnet")
    assert llm_cfg.provider == "anthropic"

    server_cfg = ServerConfig(host="0.0.0.0", port=8080)
    assert server_cfg.port == 8080

    app_cfg = AppConfig(
        app_name="CustomApp",
        version="2.0.0",
        paths=paths,
        logging=logging_cfg,
        llm=llm_cfg,
        server=server_cfg,
    )
    data = app_cfg.to_dict()
    assert data["app_name"] == "CustomApp"

    from_dict_cfg = AppConfig.from_dict(data)
    assert from_dict_cfg.app_name == "CustomApp"
    assert from_dict_cfg.logging.level == "WARNING"
    assert from_dict_cfg.llm.provider == "anthropic"


# ---------------------------------------------------------------------------
# 5. Sources Tests
# ---------------------------------------------------------------------------

def test_sources(tmp_path, monkeypatch):
    defaults_src = DefaultsSource()
    assert defaults_src.source_type == ConfigSource.DEFAULT
    assert defaults_src.name == "defaults"
    assert defaults_src.load()["app_name"] == "ScholarOS"

    # Missing optional file -> empty dict
    missing_file_src = FileSource(tmp_path / "missing.toml", optional=True)
    assert missing_file_src.load() == {}

    # Missing required file -> ConfigurationError
    strict_file_src = FileSource(tmp_path / "missing.toml", optional=False)
    with pytest.raises(ConfigurationError):
        strict_file_src.load()

    # Valid JSON file
    json_path = tmp_path / "config.json"
    json_path.write_text(json.dumps({"app_name": "JsonApp", "debug": True}), encoding="utf-8")
    json_src = FileSource(json_path)
    assert json_src.load() == {"app_name": "JsonApp", "debug": True}

    # Environment Source
    monkeypatch.setenv("SCHOLAROS_ENVIRONMENT", "staging")
    env_src = EnvironmentSource(prefix="SCHOLAROS_")
    assert env_src.source_type == ConfigSource.ENVIRONMENT
    assert env_src.load()["environment"] == "staging"

    # CLI Source
    cli_src = CliSource({"debug": True, "app_name": "CliApp"})
    assert cli_src.source_type == ConfigSource.COMMAND_LINE
    assert cli_src.load()["app_name"] == "CliApp"


# ---------------------------------------------------------------------------
# 6. Loader Tests
# ---------------------------------------------------------------------------

def test_loader_precedence(tmp_path, monkeypatch):
    # Setup test file
    json_file = tmp_path / "app.json"
    json_file.write_text(json.dumps({
        "app_name": "FromFile",
        "logging": {"level": "ERROR"},
    }), encoding="utf-8")

    # Setup environment
    monkeypatch.setenv("SCHOLAROS_LOGGING_LEVEL", "DEBUG")

    # CLI overrides
    overrides = {"debug": True}

    cfg = ConfigLoader.load(
        path=json_file,
        overrides=overrides,
    )

    # Defaults provides version
    assert cfg.version == "1.0.0"
    # File overrides app_name
    assert cfg.app_name == "FromFile"
    # Environment overrides file's logging level
    assert cfg.logging.level == "DEBUG"
    # CLI overrides debug
    assert cfg.debug is True


# ---------------------------------------------------------------------------
# 7. Settings Tests
# ---------------------------------------------------------------------------

def test_immutable_settings():
    config = AppConfig(app_name="ImmutableApp", version="3.0.0")
    settings = Settings.from_config(config)

    assert settings.app_name == "ImmutableApp"
    assert settings.version == "3.0.0"
    assert settings.get("app_name") == "ImmutableApp"
    assert settings.get("logging.level") == "INFO"
    assert settings.get("nonexistent.key", "default_val") == "default_val"

    # Test immutability
    with pytest.raises(AttributeError):
        settings.app_name = "Mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 8. Manager Tests
# ---------------------------------------------------------------------------

def test_config_manager():
    manager = ConfigManager()
    assert manager.config.app_name == "ScholarOS"
    assert isinstance(manager.settings, Settings)
    assert manager.get("app_name") == "ScholarOS"

    # Load overrides
    manager.load(app_name="OverriddenApp", debug=True)
    assert manager.config.app_name == "OverriddenApp"
    assert manager.settings.debug is True
    assert manager.get("debug") is True

    # Custom source
    manager.add_source(CliSource({"version": "9.9.9"}))
    assert manager.config.version == "9.9.9"
    assert manager.settings.version == "9.9.9"

    # Representation
    assert "ConfigManager" in repr(manager)


# ---------------------------------------------------------------------------
# 9. Exceptions Tests
# ---------------------------------------------------------------------------

def test_configuration_exceptions():
    assert issubclass(ConfigurationMissingError, ConfigurationError)
    assert issubclass(ConfigurationLoadError, ConfigurationError)