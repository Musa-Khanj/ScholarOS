"""
ScholarOS Plugin Service.

Kernel service responsible for managing the PluginManager lifecycle
and registering plugin components into the dependency injection container.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.core.base import ComponentMetadata
from scholaros.kernel.service import Service
from scholaros.plugins.discovery import PluginDiscovery
from scholaros.plugins.installer import PluginInstaller
from scholaros.plugins.loader import PluginLoader
from scholaros.plugins.manager import PluginManager
from scholaros.plugins.registry import PluginRegistry

if TYPE_CHECKING:
    from scholaros.container.container import Container


class PluginService(Service):
    """
    Kernel service bridging PluginManager to ScholarOS kernel and DI container.
    """

    def __init__(
        self,
        manager: PluginManager | None = None,
    ) -> None:
        super().__init__(
            ComponentMetadata(
                name="Plugin Service",
                version="1.0",
                description="Provides the ScholarOS plugin management system.",
                author="ScholarOS",
            )
        )
        self.manager = manager if manager is not None else PluginManager()
        self._running = False

    @property
    def is_running(self) -> bool:
        """Return True if plugin service is running."""
        return self._running

    def start(self) -> None:
        """Start the plugin service and activate all loaded plugins."""
        self._running = True
        self.manager.start_all()

    def stop(self) -> None:
        """Stop all plugins and pause the plugin service."""
        self._running = False
        self.manager.stop_all()

    def register_container(self, container: Any) -> None:
        """
        Register plugin services and managers into the DI container.
        Supports both scholaros.container.Container and scholaros.core.container.ServiceContainer.
        """
        if hasattr(container, "add_instance"):
            # scholaros.container.Container
            container.add_instance(PluginManager, self.manager)
            container.add_instance(PluginRegistry, self.manager.registry)
            container.add_instance(PluginLoader, self.manager.loader)
            container.add_instance(PluginDiscovery, self.manager.discovery)
            container.add_instance(PluginInstaller, self.manager.installer)
            container.add_instance(PluginService, self)
        elif hasattr(container, "register_instance"):
            # scholaros.core.container.ServiceContainer
            container.register_instance(PluginManager, self.manager)
            container.register_instance(PluginRegistry, self.manager.registry)
            container.register_instance(PluginLoader, self.manager.loader)
            container.register_instance(PluginDiscovery, self.manager.discovery)
            container.register_instance(PluginInstaller, self.manager.installer)
            container.register_instance(PluginService, self)

    @classmethod
    def configure_container(
        cls,
        container: Any,
        manager: PluginManager | None = None,
    ) -> PluginService:
        """
        Convenience factory to instantiate PluginService and wire it into container.
        """
        service = cls(manager=manager)
        service.register_container(container)
        return service


__all__ = [
    "PluginService",
]
