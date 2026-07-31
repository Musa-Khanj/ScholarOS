"""
ScholarOS
Hook

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Defines the base interface for all ScholarOS
event hooks.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class Hook(ABC):
    """
    Base class for all ScholarOS hooks.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return the hook name.
        """

    @property
    @abstractmethod
    def description(
        self,
    ) -> str:
        """
        Return a short description
        of the hook.
        """

    @property
    @abstractmethod
    def event(
        self,
    ) -> str:
        """
        Return the event handled
        by this hook.
        """

    @abstractmethod
    def execute(
        self,
        *args,
        **kwargs,
    ) -> object:
        """
        Execute the hook.
        """

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the hook.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"event={self.event!r}"
            f")"
        )