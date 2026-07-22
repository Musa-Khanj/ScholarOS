from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PluginManifest:
    name: str
    version: str
    author: str
    description: str

    scholaros: str

    license: str