"""
ScholarOS Plugin Sandbox.

Defines execution isolation abstractions and default execution environments
for ScholarOS plugins.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from scholaros.plugins.permissions import PermissionManager


class PluginSandbox(ABC):
    """
    Abstract interface for isolated plugin execution environments.
    """

    @abstractmethod
    def execute(self, target: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Execute a target callable within the sandbox environment.
        """

    @abstractmethod
    def is_allowed(self, action: str) -> bool:
        """
        Check if a given action or system call is allowed by the sandbox.
        """


class DefaultSandbox(PluginSandbox):
    """
    Default pass-through sandbox that integrates with PermissionManager.
    """

    def __init__(
        self,
        plugin_id: str | None = None,
        permission_manager: PermissionManager | None = None,
    ) -> None:
        self.plugin_id = plugin_id
        self.permission_manager = permission_manager

    def is_allowed(self, action: str) -> bool:
        """
        Check if the action/permission is allowed for this plugin.
        """
        if self.permission_manager is None or self.plugin_id is None:
            return True
        return self.permission_manager.has_permission(self.plugin_id, action)

    def execute(self, target: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Execute the target callable directly.
        """
        return target(*args, **kwargs)


__all__ = [
    "DefaultSandbox",
    "PluginSandbox",
]
