"""
ScholarOS
Service Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Registers and manages ScholarOS
services.
"""

from __future__ import annotations

from scholaros.services.service import Service


class ServiceManager:
    """
    Manages registered services.
    """

    def __init__(
        self,
    ) -> None:

        self._services: dict[str, Service] = {}

    def register(
        self,
        service: Service,
    ) -> None:
        """
        Register a service.
        """

        self._services[
            service.name
        ] = service

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
    ) -> Service:
        """
        Return the specified service.
        """

        return self._services[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Return whether the specified
        service is registered.
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
    ) -> dict[str, Service]:
        """
        Return the registered
        services.
        """

        return self._services

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the
        ServiceManager.
        """

        return (
            f"{self.__class__.__name__}("
            f"services="
            f"{len(self._services)}"
            f")"
        )