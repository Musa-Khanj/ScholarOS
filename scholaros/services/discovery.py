"""
ScholarOS Service Discovery.

Discovers service implementations through package scanning, directory inspection,
or explicit class registration.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import TYPE_CHECKING

from scholaros.services.service import Service

if TYPE_CHECKING:
    from scholaros.services.metadata import ServiceMetadata


class DiscoveredService:
    """
    Representation of a discovered service class.
    """

    def __init__(self, service_class: type[Service]) -> None:
        self.service_class = service_class
        self.name = getattr(service_class, "name", service_class.__name__)

    def instantiate(self) -> Service:
        """Instantiate the discovered service."""
        return self.service_class()

    def __repr__(self) -> str:
        return f"DiscoveredService(name={self.name!r}, class={self.service_class.__name__})"


class ServiceDiscovery:
    """
    Scans packages and modules for Service subclasses.
    """

    def discover_module(self, module_path: str) -> list[DiscoveredService]:
        """
        Scan a module or package path for Service classes.
        """
        discovered: list[DiscoveredService] = []
        try:
            mod = importlib.import_module(module_path)
        except Exception:
            return discovered

        for _, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, Service) and obj is not Service:
                discovered.append(DiscoveredService(obj))

        return discovered

    def discover_package(self, package_name: str) -> list[DiscoveredService]:
        """
        Scan all submodules of a package for Service classes.
        """
        discovered: list[DiscoveredService] = []
        try:
            pkg = importlib.import_module(package_name)
        except Exception:
            return discovered

        pkg_path = getattr(pkg, "__path__", None)
        if not pkg_path:
            return self.discover_module(package_name)

        for _, sub_name, _ in pkgutil.walk_packages(pkg_path, prefix=f"{package_name}."):
            discovered.extend(self.discover_module(sub_name))

        return discovered


__all__ = [
    "DiscoveredService",
    "ServiceDiscovery",
]
