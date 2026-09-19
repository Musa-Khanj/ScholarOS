"""
ScholarOS Platform Handling & Directory Resolution.

Provides system-standard directory paths following OS conventions:
- Windows: %APPDATA% / %LOCALAPPDATA% (Roaming configs, Local data/cache/logs)
- Linux: XDG Base Directory specification ($XDG_CONFIG_HOME, $XDG_DATA_HOME, etc.)
- macOS: ~/Library/Application Support, ~/Library/Caches, ~/Library/Logs
- Custom overrides via environment variables (SCHOLAROS_HOME, SCHOLAROS_CONFIG_DIR, etc.)
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

DEFAULT_STARTER_CONFIG = """# ScholarOS Configuration
[app]
name = "ScholarOS"
version = "1.0.0"
environment = "production"
debug = false

[ai]
default_provider = "ollama"
default_model = "qwen2.5:1.5b"
base_url = "http://localhost:11434"
temperature = 0.0
timeout_seconds = 60.0

[knowledge]
chunk_size = 1000
chunk_overlap = 200
auto_index = true

[retrieval]
strategy = "hybrid"
limit = 10
min_score = 0.0
cache_enabled = true

[gui]
theme = "system"
window_width = 1200
window_height = 800
"""


def is_windows() -> bool:
    """Return True if running on Windows."""
    return sys.platform == "win32" or os.name == "nt"


def is_macos() -> bool:
    """Return True if running on macOS (Darwin)."""
    return sys.platform == "darwin"


def get_app_dir() -> Path:
    """
    Return the primary ScholarOS application root directory.
    Respects SCHOLAROS_HOME if set.
    """
    if "SCHOLAROS_HOME" in os.environ:
        return Path(os.environ["SCHOLAROS_HOME"]).resolve()

    if is_windows():
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / "ScholarOS"
        return Path.home() / "AppData" / "Roaming" / "ScholarOS"

    if is_macos():
        return Path.home() / "Library" / "Application Support" / "ScholarOS"

    # Linux / POSIX default
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data) / "scholaros"
    return Path.home() / ".scholaros"


def get_config_dir() -> Path:
    """
    Return the configuration directory.
    Respects SCHOLAROS_CONFIG_DIR if set.
    """
    if "SCHOLAROS_CONFIG_DIR" in os.environ:
        return Path(os.environ["SCHOLAROS_CONFIG_DIR"]).resolve()

    if is_windows():
        return get_app_dir() / "config"

    if is_macos():
        return get_app_dir() / "config"

    # Linux / POSIX XDG
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "scholaros"
    return Path.home() / ".config" / "scholaros"


def get_data_dir() -> Path:
    """
    Return the persistent data storage directory (collections, vector stores, indexes).
    Respects SCHOLAROS_DATA_DIR if set.
    """
    if "SCHOLAROS_DATA_DIR" in os.environ:
        return Path(os.environ["SCHOLAROS_DATA_DIR"]).resolve()

    if is_windows():
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / "ScholarOS" / "data"
        return get_app_dir() / "data"

    if is_macos():
        return get_app_dir() / "data"

    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data) / "scholaros" / "data"
    return get_app_dir() / "data"


def get_cache_dir() -> Path:
    """
    Return the temporary cache directory.
    Respects SCHOLAROS_CACHE_DIR if set.
    """
    if "SCHOLAROS_CACHE_DIR" in os.environ:
        return Path(os.environ["SCHOLAROS_CACHE_DIR"]).resolve()

    if is_windows():
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / "ScholarOS" / "cache"
        return get_app_dir() / "cache"

    if is_macos():
        return Path.home() / "Library" / "Caches" / "ScholarOS"

    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / "scholaros"
    return Path.home() / ".cache" / "scholaros"


def get_log_dir() -> Path:
    """
    Return the application log directory.
    Respects SCHOLAROS_LOG_DIR if set.
    """
    if "SCHOLAROS_LOG_DIR" in os.environ:
        return Path(os.environ["SCHOLAROS_LOG_DIR"]).resolve()

    if is_windows():
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / "ScholarOS" / "logs"
        return get_app_dir() / "logs"

    if is_macos():
        return Path.home() / "Library" / "Logs" / "ScholarOS"

    xdg_state = os.environ.get("XDG_STATE_HOME")
    if xdg_state:
        return Path(xdg_state) / "scholaros" / "logs"
    return get_app_dir() / "logs"


def get_default_config_path() -> Path:
    """Return the canonical config file path."""
    return get_config_dir() / "config.toml"


def ensure_app_directories() -> dict[str, Path]:
    """
    Create all standard application directories if they do not already exist.
    """
    dirs = {
        "app": get_app_dir(),
        "config": get_config_dir(),
        "data": get_data_dir(),
        "cache": get_cache_dir(),
        "logs": get_log_dir(),
    }
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)
    return dirs


def initialize_user_environment(force: bool = False) -> dict[str, Path]:
    """
    Bootstrap user configuration, directories, and default starter files.
    """
    dirs = ensure_app_directories()
    config_file = get_default_config_path()

    if force or not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(DEFAULT_STARTER_CONFIG, encoding="utf-8")

    dirs["config_file"] = config_file
    return dirs


__all__ = [
    "DEFAULT_STARTER_CONFIG",
    "ensure_app_directories",
    "get_app_dir",
    "get_cache_dir",
    "get_config_dir",
    "get_data_dir",
    "get_default_config_path",
    "get_log_dir",
    "initialize_user_environment",
    "is_macos",
    "is_windows",
]
