"""
ScholarOS
Container Builder

Version : 1.0
Status  : Frozen
Python  : 3.14+

Author  : ScholarOS Framework

Description
-----------
Responsible for constructing object graphs through
constructor dependency injection.

The Builder is intentionally unaware of service
lifetimes (Singleton, Scoped, Transient). Lifetime
management belongs to the Container and Scope.

Responsibilities
----------------
• Inspect constructors
• Cache reflection metadata
• Resolve constructor dependencies
• Detect circular dependencies
• Construct objects
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, TypeAlias, get_type_hints

from scholaros.container.exceptions import (
    CircularDependencyError,
    InvalidServiceError,
)

Resolver: TypeAlias = Callable[[type], Any]


class Builder:
    """
    Constructs dependency graphs for registered services.

    This class performs constructor injection only.
    It never stores instances and never manages service
    lifetimes.
    """

    def __init__(
        self,
        resolver: Resolver,
    ) -> None:
        """
        Initialize the Builder.

        Parameters
        ----------
        resolver:
            Function used to resolve constructor
            dependencies from the container.
        """

        self._resolver = resolver

        #
        # Reflection caches
        #

        self._signature_cache: dict[
            type,
            inspect.Signature,
        ] = {}

        self._parameter_cache: dict[
            type,
            list[inspect.Parameter],
        ] = {}

        self._type_hints_cache: dict[
            type,
            dict[str, Any],
        ] = {}

        #
        # Circular dependency detection
        #

        self._building: list[type] = []

    def build(
        self,
        implementation: type,
    ) -> Any:
        """
        Construct an instance of the given implementation.
        This method coordinates the complete object
        construction pipeline while protecting against
        circular dependencies.
        """

        self._enter_build(implementation)

        try:

            kwargs = self._resolve_parameters(
                implementation
            )

            instance = implementation(
                **kwargs
            )

        finally:

            self._exit_build()

        return instance

    def _enter_build(
        self,
        implementation: type,
    ) -> None:
        """
        Begin constructing an implementation.

        Raises
        ------
        CircularDependencyError
            If the implementation already exists in
            the current construction path.
        """

        if implementation in self._building:

            cycle = " -> ".join(
                cls.__name__
                for cls in (
                    *self._building,
                    implementation,
                )
            )

            raise CircularDependencyError(cycle)

        self._building.append(
            implementation
        )

    def _exit_build(self) -> None:
        """
        Finish the current construction operation.
        """

        self._building.pop()
    def _get_signature(
        self,
        implementation: type,
    ) -> inspect.Signature:
        """
        Return the cached constructor signature.
        """

        signature = self._signature_cache.get(
            implementation
        )

        if signature is None:

            signature = inspect.signature(
                implementation.__init__
            )

            self._signature_cache[
                implementation
            ] = signature

        return signature

    def _get_parameters(
        self,
        implementation: type,
    ) -> list[inspect.Parameter]:
        """
        Return the cached constructor parameters.

        Excludes:
        • self
        • *args
        • **kwargs
        """

        parameters = self._parameter_cache.get(
            implementation
        )

        if parameters is None:

            signature = self._get_signature(
                implementation
            )

            parameters = [
                parameter
                for parameter in signature.parameters.values()
                if (
                    parameter.name != "self"
                    and parameter.kind
                    not in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    )
                )
            ]

            self._parameter_cache[
                implementation
            ] = parameters

        return parameters

    def _get_type_hints(
        self,
        implementation: type,
    ) -> dict[str, Any]:
        """
        Return cached constructor type hints.

        Supports postponed annotations through
        typing.get_type_hints().
        """

        hints = self._type_hints_cache.get(
            implementation
        )

        if hints is None:

            hints = get_type_hints(
                implementation.__init__
            )

            self._type_hints_cache[
                implementation
            ] = hints

        return hints

    def _resolve_parameters(
        self,
        implementation: type,
    ) -> dict[str, Any]:
        """
        Resolve all constructor dependencies.

        Parameters with default values are considered
        configuration values and are not resolved
        through the container.
        """

        parameters = self._get_parameters(
            implementation
        )

        type_hints = self._get_type_hints(
            implementation
        )

        kwargs: dict[str, Any] = {}

        for parameter in parameters:

            annotation = type_hints.get(
                parameter.name,
                parameter.annotation,
            )

            if annotation is inspect.Parameter.empty:

                raise InvalidServiceError(
                    f"{implementation.__name__}."
                    f"{parameter.name} "
                    "has no type annotation."
                )

            #
            # Parameters with default values are treated
            # as configuration values rather than
            # container-managed services.
            #

            if (
                parameter.default
                is not inspect.Parameter.empty
            ):
                continue

            kwargs[
                parameter.name
            ] = self._resolver(
                annotation
            )

        return kwargs