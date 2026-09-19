from __future__ import annotations

from typing import Any

from scholaros.tools.registry import ToolRegistry
from scholaros.tools.result import ToolResult
from scholaros.tools.tool import Tool


class ToolManager:
    """
    Manages the lifecycle of ScholarOS tools.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
    ) -> None:
        """
        Initialize the tool manager.
        """

        self._registry = registry or ToolRegistry()

    @property
    def registry(
        self,
    ) -> ToolRegistry:
        """
        Return the configured tool registry.
        """

        return self._registry

    def register(
        self,
        tool: Tool,
    ) -> None:
        """
        Register a tool.
        """

        self._registry.add(tool)

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Unregister a tool.
        """

        self._registry.remove(name)

    def get(
        self,
        name: str,
    ) -> Tool:
        """
        Return a registered tool.
        """

        return self._registry.get(name)

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return True if the tool exists.
        """

        return self._registry.contains(name)

    def installed(
        self,
    ) -> list[str]:
        """
        Return the registered tool names.
        """

        return self._registry.names()

    def enable(
        self,
        name: str,
    ) -> None:
        """
        Enable a tool.
        """

        self.get(name).enable()

    def disable(
        self,
        name: str,
    ) -> None:
        """
        Disable a tool.
        """

        self.get(name).disable()

    def get_tool(
        self,
        name: str,
    ) -> Tool | None:
        """
        Return a registered tool or None if not found.
        """
        if self.contains(name):
            return self.get(name)
        return None

    def list_tools(
        self,
        enabled_only: bool = False,
    ) -> list[Tool]:
        """
        Return list of all registered tools, optionally filtering by enabled status.
        """
        tools = [self.get(n) for n in self._registry.names()]
        if enabled_only:
            return [t for t in tools if t.is_enabled]
        return tools

    def execute(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute a registered tool.
        """
        if not self.contains(name):
            return ToolResult(
                success=False,
                error=f"Tool '{name}' not found.",
            )

        return self.get(name).execute(
            *args,
            **kwargs,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered tools.
        """

        self._registry.clear()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the tool manager.
        """

        return (
            f"{self.__class__.__name__}("
            f"tools={self.registry.size}"
            f")"
        )
