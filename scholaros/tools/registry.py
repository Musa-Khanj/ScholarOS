from __future__ import annotations

from scholaros.tools.tool import Tool


class ToolRegistry:
    """
    Stores the registered ScholarOS tools.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize an empty tool registry.
        """

        self._tools: dict[str, Tool] = {}

    def add(
        self,
        tool: Tool,
    ) -> None:
        """
        Register a tool.
        """

        self._tools[tool.name] = tool

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a registered tool.
        """

        self._tools.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> Tool:
        """
        Return a registered tool.
        """

        return self._tools[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return True if the tool exists.
        """

        return name in self._tools

    def names(
        self,
    ) -> list[str]:
        """
        Return the registered tool names.
        """

        return sorted(self._tools)

    def values(
        self,
    ) -> list[Tool]:
        """
        Return the registered tools.
        """

        return list(self._tools.values())

    def items(
        self,
    ) -> list[tuple[str, Tool]]:
        """
        Return the registered tool items.
        """

        return list(self._tools.items())

    def clear(
        self,
    ) -> None:
        """
        Remove all registered tools.
        """

        self._tools.clear()

    @property
    def size(
        self,
    ) -> int:
        """
        Return the number of registered tools.
        """

        return len(self._tools)

    @property
    def tools(
        self,
    ) -> dict[str, Tool]:
        """
        Return the registered tools.
        """

        return self._tools

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the registry.
        """

        return (
            f"{self.__class__.__name__}("
            f"tools={self.size}"
            f")"
        )