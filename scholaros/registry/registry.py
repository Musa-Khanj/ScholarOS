"""
ScholarOS
Service Registry

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides a central registry for
ScholarOS services and components.
"""

from __future__ import annotations

from typing import Any


class ServiceRegistry:
    """
    Central registry for ScholarOS
    services.
    """

    def __init__(
        self,
    ) -> None:

        self._services: dict[str, Any] = {}

    def register(
        self,
        name: str,
        service: Any,
    ) -> None:
        """
        Register a service.
        """

        self._services[name] = service

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Unregister a service.
        """

        self._services.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> Any:
        """
        Return a registered service.
        """

        return self._services[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether a service is
        registered.
        """

        return (
            name
            in self._services
        )

    def registered(
        self,
    ) -> list[str]:
        """
        Return registered service
        names.
        """

        return sorted(
            self._services,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all registered
        services.
        """

        self._services.clear()

    @property
    def services(
        self,
    ) -> dict[str, Any]:
        """
        Return all registered
        services.
        """

        return self._services

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"services="
            f"{len(self._services)}"
            f")"
        )