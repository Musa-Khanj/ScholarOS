"""
ScholarOS
Extension

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Defines the base interface for all
ScholarOS extensions.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class Extension(ABC):
    """
    Base class for all ScholarOS
    extensions.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return the extension name.
        """

    @property
    @abstractmethod
    def description(
        self,
    ) -> str:
        """
        Return a short description
        of the extension.
        """

    @property
    @abstractmethod
    def version(
        self,
    ) -> str:
        """
        Return the extension version.
        """

    @property
    @abstractmethod
    def enabled(
        self,
    ) -> bool:
        """
        Return whether the extension
        is enabled.
        """

    @abstractmethod
    def enable(
        self,
    ) -> None:
        """
        Enable the extension.
        """

    @abstractmethod
    def disable(
        self,
    ) -> None:
        """
        Disable the extension.
        """

    @abstractmethod
    def execute(
        self,
        *args,
        **kwargs,
    ) -> object:
        """
        Execute the extension.
        """

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the extension.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"enabled={self.enabled!r}"
            f")"
        )