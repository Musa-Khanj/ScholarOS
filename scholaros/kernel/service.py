from __future__ import annotations

from abc import ABC, abstractmethod

from scholaros.core.base import Component


class Service(Component, ABC):
    @abstractmethod
    def start(self) -> None:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...