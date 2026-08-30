"""
ScholarOS
Service Container

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides dependency injection for ScholarOS.

The ServiceContainer is responsible for
registering, constructing, and resolving
application services.

Supported registrations

- Singleton
- Transient
- Existing Instance
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

Factory = Callable[[], Any]


class ServiceContainer:
    """
    Dependency Injection container.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the container.
        """

        self._singletons: dict[
            object,
            Factory,
        ] = {}

        self._singleton_instances: dict[
            object,
            Any,
        ] = {}

        self._transients: dict[
            object,
            Factory,
        ] = {}

        self._instances: dict[
            object,
            Any,
        ] = {}

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register_singleton(
        self,
        service: object,
        factory: Factory,
    ) -> None:
        """
        Register a singleton factory.
        """

        if not callable(factory):
            raise TypeError(
                "Factory must be callable."
            )

        self._singletons[service] = factory

    def register_transient(
        self,
        service: object,
        factory: Factory,
    ) -> None:
        """
        Register a transient factory.
        """

        if not callable(factory):
            raise TypeError(
                "Factory must be callable."
            )

        self._transients[service] = factory

    def register_instance(
        self,
        service: object,
        instance: Any,
    ) -> None:
        """
        Register an existing instance.
        """

        self._instances[
            service
        ] = instance

    # ---------------------------------------------------------
    # Resolution
    # ---------------------------------------------------------

    def resolve(
        self,
        service: object,
    ) -> Any:
        """
        Resolve a service.
        """

        if service in self._instances:
            return self._instances[
                service
            ]

        if service in self._singleton_instances:
            return self._singleton_instances[
                service
            ]

        if service in self._singletons:

            instance = self._singletons[
                service
            ]()

            self._singleton_instances[
                service
            ] = instance

            return instance

        if service in self._transients:
            return self._transients[
                service
            ]()

        raise LookupError(
            f"Service not registered: "
            f"{service!r}"
        )

    # ---------------------------------------------------------
    # Maintenance
    # ---------------------------------------------------------

    def remove(
        self,
        service: object,
    ) -> bool:
        """
        Remove a registration.

        Returns
        -------
        bool
            True if removed.
        """

        removed = False

        removed |= (
            self._instances.pop(
                service,
                None,
            )
            is not None
        )

        removed |= (
            self._singleton_instances.pop(
                service,
                None,
            )
            is not None
        )

        removed |= (
            self._singletons.pop(
                service,
                None,
            )
            is not None
        )

        removed |= (
            self._transients.pop(
                service,
                None,
            )
            is not None
        )

        return removed

    def clear(
        self,
    ) -> None:
        """
        Remove every registration.
        """

        self._instances.clear()

        self._singleton_instances.clear()

        self._singletons.clear()

        self._transients.clear()

    # ---------------------------------------------------------
    # Introspection
    # ---------------------------------------------------------

    def contains(
        self,
        service: object,
    ) -> bool:
        """
        Return True if registered.
        """

        return (
            service in self._instances
            or service in self._singletons
            or service in self._transients
        )

    def services(
        self,
    ) -> tuple[object, ...]:
        """
        Return registered services.
        """

        values = (
            set(self._instances)
            | set(self._singletons)
            | set(self._transients)
        )

        return tuple(values)

    # ---------------------------------------------------------
    # Magic Methods
    # ---------------------------------------------------------

    def __contains__(
        self,
        service: object,
    ) -> bool:
        """
        Support

            if EventBus in container:
        """

        return self.contains(
            service,
        )

    def __len__(
        self,
    ) -> int:
        """
        Number of registered services.
        """

        return len(
            self.services()
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"services={len(self)}"
            f")"
        )