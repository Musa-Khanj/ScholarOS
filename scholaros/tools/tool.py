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
from collections.abc import Callable
from typing import Any

from scholaros.tools.manifest import ToolManifest
from scholaros.tools.result import ToolResult


class Tool(ABC):
    """
    Base class for all ScholarOS tools.
    """

    manifest: ToolManifest
    _enabled: bool = True

    @abstractmethod
    def execute(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute the tool.
        """

    @property
    def is_enabled(self) -> bool:
        """
        Return whether the tool is enabled.
        """
        return getattr(self, "_enabled", True)

    def enable(
        self,
    ) -> None:
        """
        Enable the tool.
        """
        self._enabled = True

    def disable(
        self,
    ) -> None:
        """
        Disable the tool.
        """
        self._enabled = False

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
        Return a developer-friendly representation of the tool.
        """
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}"
            f")"
        )


class FunctionTool(Tool):
    """
    Concrete tool that wraps a Python callable into a standard ScholarOS Tool.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        name: str | None = None,
        description: str | None = None,
        version: str = "1.0.0",
        author: str = "ScholarOS",
        license: str = "MIT",
        scholaros: str = ">=1.0.0",
    ) -> None:
        tool_name = str(name) if name else str(getattr(func, "__name__", "function_tool"))
        tool_desc = str(description) if description else (func.__doc__.strip() if func.__doc__ else f"Tool {tool_name}")
        self._func = func
        self.manifest = ToolManifest(
            name=tool_name,
            version=version,
            author=author,
            description=tool_desc,
            scholaros=scholaros,
            license=license,
        )
        self._enabled = True

    @classmethod
    def from_function(
        cls,
        func: Callable[..., Any],
        name: str | None = None,
        description: str | None = None,
        version: str = "1.0.0",
        **kwargs: Any,
    ) -> FunctionTool:
        """Construct a FunctionTool from a callable."""
        return cls(func, name=name, description=description, version=version, **kwargs)

    def execute(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> ToolResult:
        if not self.is_enabled:
            return ToolResult(
                success=False,
                error=f"Tool '{self.name}' is currently disabled.",
            )
        try:
            output = self._func(*args, **kwargs)
            return ToolResult(success=True, output=output)
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


__all__ = [
    "FunctionTool",
    "Tool",
]
