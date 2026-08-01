from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ToolManifest:
    name: str
    version: str
    author: str
    description: str

    scholaros: str

    license: str