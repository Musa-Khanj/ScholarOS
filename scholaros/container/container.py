"""
ScholarOS
Dependency Injection Container

Version : 1.0
Status  : Frozen
Python  : 3.14+

Author  : ScholarOS Framework

Description
-----------
Root Dependency Injection Container.

The Container is responsible for:

• Service registration
• Service resolution
• Singleton lifetime management
• Scope creation

Object construction is delegated to Builder.

Responsibilities
----------------
• Register services
• Resolve services
• Create scopes
• Own singleton instances
• Own the service registry

The Container never performs constructor inspection
or dependency graph construction directly.
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
from scholaros.container.scope import Scope


class Container:
    """
    Root dependency injection container.

    Responsible for registration, singleton lifetime
    management and scope creation.
    """

    def __init__(self) -> None:

        #
        # Global service registry
        #

        self.registry = ServiceRegistry()

        #
        # Object builder
        #

        self.builder = Builder(
            resolver=self.resolve,
        )

    def add_singleton(
        self,
        interface: type,
        implementation: type,
    ) -> None:
        """
        Register a singleton service.
        """

        self.registry.register(
            interface,
            implementation,
            ServiceLifetime.SINGLETON,
        )

    def add_transient(
        self,
        interface: type,
        implementation: type,
    ) -> None:
        """
        Register a transient service.
        """

        self.registry.register(
            interface,
            implementation,
            ServiceLifetime.TRANSIENT,
        )

    def add_scoped(
        self,
        interface: type,
        implementation: type,
    ) -> None:
        """
        Register a scoped service.
        """

        self.registry.register(
            interface,
            implementation,
            ServiceLifetime.SCOPED,
        )

    def create_scope(self) -> Scope:
        """
        Create a new dependency injection scope.
        """

        return Scope(
            registry=self.registry,
            builder=self.builder,
        )

    def resolve(self, service_type: type) -> Any:
        """
        Resolve a registered service.

        Singleton services are cached by the root
        container. Scoped services must be resolved
        through a Scope.
        """

        if not self.registry.contains(
            service_type
        ):
            raise ServiceNotFound(
                service_type.__name__
            )

        descriptor = self.registry.get(
            service_type
        )

        #
        # Singleton lifetime
        #

        if (
            descriptor.lifetime
            == ServiceLifetime.SINGLETON
        ):

            if descriptor.instance is None:

                descriptor.instance = (
                    self.builder.build(
                        descriptor.implementation
                    )
                )

            return descriptor.instance

        #
        # Scoped lifetime
        #

        if (
            descriptor.lifetime
            == ServiceLifetime.SCOPED
        ):

            raise RuntimeError(
                "Scoped services must be resolved "
                "from a Scope."
            )

        #
        # Transient lifetime
        #

        return self.builder.build(
            descriptor.implementation
        )

    @property
    def services(self) -> ServiceRegistry:
        """
        Exposes the service registry.

        This property is intended for framework
        diagnostics and unit testing.
        """

        return self.registry