from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scholaros.container.lifetime import ServiceLifetime


@dataclass(slots=True)
class ServiceDescriptor:
    interface: type
    implementation: type
    lifetime: ServiceLifetime
    instance: Any | None = None