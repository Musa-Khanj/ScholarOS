"""
ScholarOS
Tool

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Defines the base interface for all
ScholarOS tools.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from scholaros.tools.manifest import ToolManifest
from scholaros.tools.result import ToolResult


class Tool(ABC):
    """
    Base class for all ScholarOS tools.
    """

    manifest: ToolManifest

    @abstractmethod
    def execute(
        self,
        *args,
        **kwargs,
    ) -> ToolResult:
        """
        Execute the tool.
        """

    @abstractmethod
    def enable(
        self,
    ) -> None:
        """
        Enable the tool.
        """

    @abstractmethod
    def disable(
        self,
    ) -> None:
        """
        Disable the tool.
        """

    @property
    def name(
        self,
    ) -> str:
        """
        Return the tool name.
        """

        return self.manifest.name

    @property
    def version(
        self,
    ) -> str:
        """
        Return the tool version.
        """

        return self.manifest.version

    @property
    def description(
        self,
    ) -> str:
        """
        Return the tool description.
        """

        return self.manifest.description

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the tool.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}"
            f")"
        )