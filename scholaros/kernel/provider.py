from __future__ import annotations

from dataclasses import dataclass
from typing import Generic
from typing import TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class ServiceProvider(Generic[T]):
    interface: type[T]
    implementation: T
    singleton: bool = True
    name: str | None = None