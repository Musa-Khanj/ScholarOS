"""
ScholarOS
GUI Component

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Defines the abstract base class for all
ScholarOS GUI components.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GUIComponent(ABC):
    """
    Abstract base class for all GUI
    components.
    """

    def __init__(
        self,
        parent: Any,
    ) -> None:
        """
        Initialize the component.
        """

        self._parent = parent

    @property
    def parent(
        self,
    ) -> Any:
        """
        Return the parent object.
        """

        return self._parent

    @abstractmethod
    def build(
        self,
    ) -> None:
        """
        Build the component.
        """

    @abstractmethod
    def refresh(
        self,
    ) -> None:
        """
        Refresh the component.
        """

    @abstractmethod
    def destroy(
        self,
    ) -> None:
        """
        Destroy the component.
        """

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"parent={self.parent!r}"
            f")"
        )