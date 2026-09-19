"""
ScholarOS Plugin Permissions.

Provides declarative permissions and a policy engine for the plugin security layer.
"""

from __future__ import annotations

from enum import Enum
from typing import Iterable

from scholaros.plugins.exceptions import PermissionError


class Permission(str, Enum):
    """
    Standard capability permissions for ScholarOS plugins.
    """

    FILESYSTEM = "filesystem"
    NETWORK = "network"
    AI = "ai"
    RESEARCH = "research"
    CONTAINER = "container"
    EVENTS = "events"
    SCHEDULER = "scheduler"
    ALL = "*"

    @classmethod
    def from_string(cls, value: str) -> Permission:
        """Parse string to Permission enum if possible."""
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        return cls(normalized)


class PermissionManager:
    """
    Manages and enforces plugin permissions and security policies.
    """

    def __init__(self, default_allow: bool = True) -> None:
        """
        Initialize PermissionManager.
        If default_allow is True, plugins default to having requested permissions granted.
        If False, permissions must be explicitly granted.
        """
        self.default_allow = default_allow
        self._granted: dict[str, set[str]] = {}

    def grant(self, plugin_id: str, permissions: Iterable[str | Permission]) -> None:
        """Grant specified permissions to a plugin."""
        if plugin_id not in self._granted:
            self._granted[plugin_id] = set()
        for p in permissions:
            val = p.value if isinstance(p, Permission) else str(p).lower()
            self._granted[plugin_id].add(val)

    def revoke(self, plugin_id: str, permissions: Iterable[str | Permission]) -> None:
        """Revoke specified permissions from a plugin."""
        if plugin_id in self._granted:
            for p in permissions:
                val = p.value if isinstance(p, Permission) else str(p).lower()
                self._granted[plugin_id].discard(val)

    def get_granted(self, plugin_id: str) -> set[str]:
        """Return granted permissions for a plugin."""
        return set(self._granted.get(plugin_id, set()))

    def has_permission(self, plugin_id: str, permission: str | Permission) -> bool:
        """Check if a plugin has a specific permission."""
        perm_str = permission.value if isinstance(permission, Permission) else str(permission).lower()
        granted = self._granted.get(plugin_id)
        if granted is not None:
            if "*" in granted or perm_str in granted:
                return True
            return False
        # If not explicitly configured, fall back to default policy
        return self.default_allow

    def check(self, plugin_id: str, permission: str | Permission) -> None:
        """
        Ensure plugin has permission or raise PermissionError.
        """
        if not self.has_permission(plugin_id, permission):
            perm_name = permission.value if isinstance(permission, Permission) else str(permission)
            raise PermissionError(
                f"Permission denied: plugin {plugin_id!r} lacks required permission '{perm_name}'."
            )

    def validate_plugin(self, plugin_id: str, required_permissions: Iterable[str | Permission]) -> None:
        """
        Verify that all required permissions of a plugin are granted.
        """
        missing: list[str] = []
        for p in required_permissions:
            if not self.has_permission(plugin_id, p):
                val = p.value if isinstance(p, Permission) else str(p)
                missing.append(val)

        if missing:
            raise PermissionError(
                f"Plugin {plugin_id!r} lacks authorized permissions: {', '.join(missing)}."
            )

    def clear(self) -> None:
        """Clear all granted permissions."""
        self._granted.clear()


__all__ = [
    "Permission",
    "PermissionManager",
]
