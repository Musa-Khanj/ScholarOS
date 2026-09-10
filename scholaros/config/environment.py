"""
ScholarOS Environment Configuration.

The sole module in the ScholarOS configuration subsystem responsible
for reading, parsing, and type-casting os.environ variables.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class EnvironmentReader:
    """
    Reads, parses, and type-casts environment variables from os.environ.
    """

    def __init__(self, prefix: str = "SCHOLAROS_") -> None:
        self._prefix = prefix

    @property
    def prefix(self) -> str:
        return self._prefix

    def get(self, key: str, default: str | None = None) -> str | None:
        """Read a raw environment variable."""
        return os.environ.get(key, default)

    def get_str(self, key: str, default: str = "") -> str:
        """Get an environment variable as a string."""
        return os.environ.get(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        """Get an environment variable parsed as an integer."""
        val = os.environ.get(key)
        if val is None:
            return default
        try:
            return int(val.strip())
        except ValueError:
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get an environment variable parsed as a float."""
        val = os.environ.get(key)
        if val is None:
            return default
        try:
            return float(val.strip())
        except ValueError:
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get an environment variable parsed as a boolean."""
        val = os.environ.get(key)
        if val is None:
            return default
        return val.strip().lower() in ("1", "true", "yes", "on")

    def get_path(self, key: str, default: Path | None = None) -> Path:
        """Get an environment variable parsed as a Path."""
        val = os.environ.get(key)
        if val is None:
            return default if default is not None else Path()
        return Path(val.strip())

    KNOWN_SECTIONS = frozenset({"paths", "logging", "llm", "server"})

    def load_prefixed(self) -> dict[str, Any]:
        """
        Scan os.environ for keys starting with prefix (default: SCHOLAROS_)
        and map them to a nested dictionary.

        Supports double underscore (SCHOLAROS_LOGGING__LEVEL) or standard
        section prefix matching (SCHOLAROS_LOGGING_LEVEL).
        """
        result: dict[str, Any] = {}
        prefix_len = len(self._prefix)

        for env_key, value in os.environ.items():
            if not env_key.startswith(self._prefix):
                continue

            clean_key = env_key[prefix_len:].lower()
            if not clean_key:
                continue

            parsed_value = self._parse_value(value)

            if "__" in clean_key:
                section, key = clean_key.split("__", 1)
                section_dict = result.setdefault(section, {})
                if isinstance(section_dict, dict):
                    section_dict[key] = parsed_value
                continue

            parts = clean_key.split("_")
            if len(parts) > 1 and parts[0] in self.KNOWN_SECTIONS:
                section = parts[0]
                key = "_".join(parts[1:])
                section_dict = result.setdefault(section, {})
                if isinstance(section_dict, dict):
                    section_dict[key] = parsed_value
            else:
                result[clean_key] = parsed_value

        return result

    @staticmethod
    def _parse_value(value: str) -> Any:
        """Auto-cast string values to bool, int, float, or str."""
        stripped = value.strip()
        lower = stripped.lower()
        if lower in ("true", "yes", "on"):
            return True
        if lower in ("false", "no", "off"):
            return False
        try:
            return int(stripped)
        except ValueError:
            pass
        try:
            return float(stripped)
        except ValueError:
            pass
        return stripped


_default_reader = EnvironmentReader()


def get_env(key: str, default: Any = None) -> Any:
    """Read a raw environment variable."""
    return _default_reader.get(key, default)


def load_environment(prefix: str = "SCHOLAROS_") -> dict[str, Any]:
    """Read all environment variables with the given prefix."""
    return EnvironmentReader(prefix=prefix).load_prefixed()
