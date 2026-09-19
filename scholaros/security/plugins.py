"""
ScholarOS Plugin Security & Capability Sandboxing.

Validates plugin manifests, enforces declarative capability boundaries,
and intercepts unpermitted subsystem invocations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scholaros.plugins.manifest import PluginManifest
from scholaros.plugins.permissions import Permission, PermissionManager
from scholaros.plugins.sandbox import DefaultSandbox
from scholaros.security.exceptions import CapabilityViolationError


STANDARD_CAPABILITIES = frozenset({
    "filesystem",
    "network",
    "ai",
    "research",
    "container",
    "events",
    "scheduler",
    "*",
})


def validate_plugin_manifest(
    manifest: PluginManifest | dict[str, Any],
    allowed_capabilities: set[str] | None = None,
) -> list[str]:
    """
    Validate plugin manifest properties and requested capabilities.

    Parameters
    ----------
    manifest : PluginManifest | dict[str, Any]
        The parsed plugin manifest or raw dictionary.
    allowed_capabilities : set[str] | None
        Optional whitelist of permitted capabilities.

    Returns
    -------
    list[str]
        List of validation violation messages. Empty if valid.
    """
    issues: list[str] = []

    if isinstance(manifest, dict):
        name = str(manifest.get("name", "")).strip()
        version = str(manifest.get("version", "")).strip()
        p_id = str(manifest.get("id", "")).strip()
        permissions = manifest.get("permissions", [])
    else:
        name = manifest.name.strip() if manifest.name else ""
        version = manifest.version.strip() if manifest.version else ""
        p_id = manifest.id.strip() if manifest.id else ""
        permissions = manifest.permissions

    if not name:
        issues.append("Manifest 'name' cannot be empty.")
    if not version:
        issues.append("Manifest 'version' cannot be empty.")
    if not p_id:
        issues.append("Manifest 'id' cannot be empty.")

    # Validate requested permissions
    for perm in permissions:
        perm_str = perm.value if isinstance(perm, Permission) else str(perm).lower()
        if perm_str not in STANDARD_CAPABILITIES:
            issues.append(f"Unknown or non-standard capability requested: '{perm_str}'.")
        if allowed_capabilities is not None and perm_str not in allowed_capabilities and "*" not in allowed_capabilities:
            issues.append(f"Forbidden capability requested: '{perm_str}'.")

    return issues


class SecureCapabilitySandbox(DefaultSandbox):
    """
    Enhanced execution sandbox enforcing strict capability checks before invocation.
    """

    def __init__(
        self,
        plugin_id: str | None = None,
        permission_manager: PermissionManager | None = None,
    ) -> None:
        super().__init__(plugin_id=plugin_id, permission_manager=permission_manager)

    def execute_with_capability(
        self,
        capability: str | Permission,
        target: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute target only if the plugin holds the required capability.
        Raises CapabilityViolationError if denied.
        """
        cap_str = capability.value if isinstance(capability, Permission) else str(capability).lower()
        if not self.is_allowed(cap_str):
            raise CapabilityViolationError(
                f"Capability violation: plugin {self.plugin_id!r} is not permitted to use '{cap_str}'."
            )
        return self.execute(target, *args, **kwargs)

    def execute_safe_with_capability(
        self,
        capability: str | Permission,
        target: Callable[..., Any],
        *args: Any,
        default: Any = None,
        **kwargs: Any,
    ) -> tuple[Any, Exception | None]:
        """
        Safely execute target with capability check, recording violations in sandbox errors.
        """
        cap_str = capability.value if isinstance(capability, Permission) else str(capability).lower()
        if not self.is_allowed(cap_str):
            exc = CapabilityViolationError(
                f"Capability violation: plugin {self.plugin_id!r} is not permitted to use '{cap_str}'."
            )
            self._errors.append(exc)
            return default, exc

        return self.execute_safe(target, *args, default=default, **kwargs)


__all__ = [
    "STANDARD_CAPABILITIES",
    "SecureCapabilitySandbox",
    "validate_plugin_manifest",
]
