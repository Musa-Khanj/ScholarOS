"""
ScholarOS
Container Scope

Version : 1.0
Status  : Frozen
Python  : 3.14+

Author  : ScholarOS Framework

Description
-----------
Represents a dependency injection scope.

A Scope owns scoped service instances while sharing
the service registry with the root container.

Responsibilities
----------------
• Resolve scoped services
• Cache scoped instances
• Delegate object construction to Builder
"""

from __future__ import annotations

from typing import Any

from scholaros.container.builder import Builder
from scholaros.container.exceptions import (
    ServiceNotFound,
)
from scholaros.container.lifetime import (
    ServiceLifetime,
)
from scholaros.container.registry import (
    ServiceRegistry,
)


class Scope:
    """
    Represents a dependency injection scope.
    """


    def __init__(
        self,
        registry: ServiceRegistry,
        builder: Builder,
    ) -> None:

        self._registry = registry

        self._builder = builder

        self._instances: dict[
            type,
            Any,
        ] = {}

    def resolve(
        self,
        interface: type,
    ) -> Any:
        """
        Resolve a service within the current scope.
        """

        if not self._registry.contains(
            interface
        ):
            raise ServiceNotFound(
                interface.__name__
            )

        descriptor = self._registry.get(
            interface
        )

        #
        # Scoped lifetime
        #

        if (
            descriptor.lifetime
            == ServiceLifetime.SCOPED
        ):

            instance = self._instances.get(
                interface
            )

            if instance is None:

                instance = self._builder.build(
                    descriptor.implementation
                )

                self._instances[
                    interface
                ] = instance

            return instance

        #
        # Transient lifetime
        #

        if (
            descriptor.lifetime
            == ServiceLifetime.TRANSIENT
        ):
            return self._builder.build(
                descriptor.implementation
            )

        #
        # Singleton lifetime
        #

        if descriptor.instance is None:

            descriptor.instance = (
                self._builder.build(
                    descriptor.implementation
                )
            )

        return descriptor.instance

    def dispose(self) -> None:
        """
        Dispose the current scope.

        Releases all scoped instances owned by
        this scope.
        """

        self._instances.clear()

    def __enter__(self) -> "Scope":
        """
        Enter the scope context.
        """

        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        """
        Exit the scope context.
        """

        self.dispose()

    @property
    def instances(self) -> dict[type, Any]:
        """
        Exposes the scoped instance cache.

        This property is intended for framework
        diagnostics and unit testing only.
        """

        return self._instances