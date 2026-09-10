from __future__ import annotations

from scholaros.core.exceptions import ConfigurationError


class ConfigurationMissingError(ConfigurationError):
    """Raised when a required configuration key or file is missing."""


class ConfigurationLoadError(ConfigurationError):
    """Raised when loading or parsing a configuration source fails."""


__all__ = [
    "ConfigurationError",
    "ConfigurationLoadError",
    "ConfigurationMissingError",
]