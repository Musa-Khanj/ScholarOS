from __future__ import annotations

import tomllib
from pathlib import Path

from scholaros.config.models import AppConfig


class ConfigLoader:

    @staticmethod
    def load(path: Path) -> AppConfig:

        if not path.exists():
            return AppConfig()

        with path.open("rb") as f:
            tomllib.load(f)

        return AppConfig()