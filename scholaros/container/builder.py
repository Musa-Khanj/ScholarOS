from __future__ import annotations

import inspect
from typing import Any, Callable

from scholaros.container.exceptions import (
    CircularDependencyError,
    InvalidServiceError,
)


class Builder:
    """
    Responsible for constructing object graphs.
    """

    def __init__(
        self,
        resolver: Callable[[type], Any],
    ) -> None:

        self._resolver = resolver

        self._building: list[type] = []

        self._signature_cache: dict[
            type,
            inspect.Signature,
        ] = {}

        self._parameter_cache: dict[
            type,
            list[inspect.Parameter],
        ] = {}

    def build(
        self,
        implementation: type,
    ) -> Any:

        if implementation in self._building:

            cycle = " -> ".join(
                cls.__name__
                for cls in (
                    *self._building,
                    implementation,
                )
            )

            raise CircularDependencyError(cycle)

        self._building.append(implementation)

        try:

            kwargs = self._resolve_parameters(
                implementation
            )

            return implementation(**kwargs)

        finally:

            self._building.pop()

    def _resolve_parameters(
        self,
        implementation: type,
    ) -> dict[str, Any]:

        parameters = self._parameter_cache.get(
            implementation
        )

        if parameters is None:

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

        kwargs: dict[str, Any] = {}

        for parameter in parameters:

            annotation = parameter.annotation

            if annotation is inspect.Parameter.empty:
                raise InvalidServiceError(
                    f"{implementation.__name__}.{parameter.name} "
                    "has no type annotation."
                )

            # Parameters with default values are treated as
            # configuration values rather than container services.
            if parameter.default is not inspect.Parameter.empty:
                continue

            kwargs[
                parameter.name
            ] = self._resolver(annotation)

        return kwargs