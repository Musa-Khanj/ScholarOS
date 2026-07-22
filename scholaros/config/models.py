from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class PathsConfig:
    workspace: Path
    cache: Path
    data: Path
    temp: Path


@dataclass(slots=True)
class LoggingConfig:
    level: str = "INFO"


@dataclass(slots=True)
class AppConfig:
    app_name: str = "ScholarOS"
    version: str = "0.1.0"

    paths: PathsConfig = field(
        default_factory=lambda: PathsConfig(
            workspace=Path("workspace"),
            cache=Path(".cache"),
            data=Path("data"),
            temp=Path(".temp"),
        )
    )

    logging: LoggingConfig = field(
        default_factory=LoggingConfig
    )