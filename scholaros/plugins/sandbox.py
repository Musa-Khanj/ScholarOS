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
    def execute_safe(
        self,
        target: Callable[..., Any],
        *args: Any,
        default: Any = None,
        **kwargs: Any,
    ) -> tuple[Any, Exception | None]:
        """
        Execute target safely, catching unhandled exceptions and returning (result, exception).
        """

    @abstractmethod
    def is_allowed(self, action: str) -> bool:
        """
        Check if a given action or system call is allowed by the sandbox.
        """


class DefaultSandbox(PluginSandbox):
    """
    Default pass-through sandbox that integrates with PermissionManager and captures errors.
    """

    def __init__(
        self,
        plugin_id: str | None = None,
        permission_manager: PermissionManager | None = None,
    ) -> None:
        self.plugin_id = plugin_id
        self.permission_manager = permission_manager
        self._errors: list[Exception] = []

    @property
    def errors(self) -> list[Exception]:
        """Return list of trapped exceptions."""
        return list(self._errors)

    @property
    def error_count(self) -> int:
        """Return total number of trapped errors."""
        return len(self._errors)

    @property
    def last_error(self) -> Exception | None:
        """Return the most recent trapped error, if any."""
        return self._errors[-1] if self._errors else None

    def clear_errors(self) -> None:
        """Clear recorded errors."""
        self._errors.clear()

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

    def execute_safe(
        self,
        target: Callable[..., Any],
        *args: Any,
        default: Any = None,
        **kwargs: Any,
    ) -> tuple[Any, Exception | None]:
        """
        Execute target safely, trapping exceptions to prevent plugin crashes from propagating.
        """
        try:
            result = self.execute(target, *args, **kwargs)
            return result, None
        except Exception as exc:
            self._errors.append(exc)
            return default, exc


__all__ = [
    "DefaultSandbox",
    "PluginSandbox",
]
