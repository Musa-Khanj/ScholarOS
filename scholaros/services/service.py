"""
ScholarOS
Service

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Defines the base interface for all
ScholarOS services.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class Service(ABC):
    """
    Base class for all ScholarOS
    services.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return the service name.
        """

    @property
    @abstractmethod
    def description(
        self,
    ) -> str:
        """
        Return a short description
        of the service.
        """

    @property
    @abstractmethod
    def version(
        self,
    ) -> str:
        """
        Return the service version.
        """

    @property
    @abstractmethod
    def enabled(
        self,
    ) -> bool:
        """
        Return whether the service
        is enabled.
        """

    @abstractmethod
    def start(
        self,
    ) -> None:
        """
        Start the service.
        """

    @abstractmethod
    def stop(
        self,
    ) -> None:
        """
        Stop the service.
        """

    @abstractmethod
    def execute(
        self,
        *args,
        **kwargs,
    ) -> object:
        """
        Execute the service.
        """

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the service.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"enabled={self.enabled!r}"
            f")"
        )