"""
ScholarOS
Base Agent

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Defines the abstract foundation for all
ScholarOS agents.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class BaseAgent(ABC):
    """
    Abstract base class for all ScholarOS agents.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return the agent name.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def description(
        self,
    ) -> str:
        """
        Return a short description of the agent.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def version(
        self,
    ) -> str:
        """
        Return the agent version.
        """

        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
    ) -> object:
        """
        Execute the agent's primary task.
        """

        raise NotImplementedError

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation
        of the agent.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}"
            f")"
        )