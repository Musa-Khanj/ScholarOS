from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class KernelContext:
    root_path: Path
    workspace: Path
    config_path: Path
    data_path: Path
    cache_path: Path
    temp_path: Path