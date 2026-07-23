from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Final


class ComponentStatus(str, Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass(slots=True, frozen=True)
class ComponentMetadata:
    name: str
    version: str
    description: str
    author: str


class Component(ABC):
    API_VERSION: Final[str] = "1.0"

    def __init__(self, metadata: ComponentMetadata) -> None:
        self._metadata = metadata
        self._status = ComponentStatus.CREATED

    @property
    def metadata(self) -> ComponentMetadata:
        return self._metadata

    @property
    def status(self) -> ComponentStatus:
        return self._status

    @property
    def name(self) -> str:
        return self._metadata.name

    @property
    def version(self) -> str:
        return self._metadata.version

    @property
    def description(self) -> str:
        return self._metadata.description

    @property
    def author(self) -> str:
        return self._metadata.author

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def shutdown(self) -> None:
        ...

    @abstractmethod
    def health(self) -> bool:
        ...

    def _set_status(self, status: ComponentStatus) -> None:
        self._status = status

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"status={self.status.value!r})"
        )