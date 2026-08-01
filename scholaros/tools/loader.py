from __future__ import annotations

from scholaros.tools.manager import ToolManager
from scholaros.tools.tool import Tool


class ToolLoader:
    """
    Loads and unloads ScholarOS tools.
    """

    def __init__(
        self,
        manager: ToolManager,
    ) -> None:
        """
        Initialize the tool loader.
        """

        self._manager = manager

    @property
    def manager(
        self,
    ) -> ToolManager:
        """
        Return the configured tool manager.
        """

        return self._manager

    def load(
        self,
        tool: Tool,
    ) -> None:
        """
        Load a tool.
        """

        self._manager.register(tool)

    def unload(
        self,
        name: str,
    ) -> None:
        """
        Unload a tool.
        """

        self._manager.unregister(name)

    def reload(
        self,
        tool: Tool,
    ) -> None:
        """
        Reload a tool.
        """

        self.unload(tool.name)
        self.load(tool)

    def discover(
        self,
    ) -> list[str]:
        """
        Return the discovered tools.
        """

        return self._manager.installed()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the tool loader.
        """

        return (
            f"{self.__class__.__name__}("
            f"tools={len(self.discover())}"
            f")"
        )