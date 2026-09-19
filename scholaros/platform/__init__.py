"""
ScholarOS Platform Subsystem.

Provides OS-specific path resolution, directory lifecycle management,
and environment initialization for Windows, Linux, and macOS.
"""

from __future__ import annotations

from scholaros.platform.paths import (
    DEFAULT_STARTER_CONFIG,
    ensure_app_directories,
    get_app_dir,
    get_cache_dir,
    get_config_dir,
    get_data_dir,
    get_default_config_path,
    get_log_dir,
    initialize_user_environment,
    is_macos,
    is_windows,
)

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
