"""
ScholarOS Service Descriptor.

Stores runtime service descriptions, factory bindings, dependency specifications,
and registration metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from scholaros.services.diagnostics import ServiceDiagnostics
from scholaros.services.metadata import ServiceMetadata

if TYPE_CHECKING:
    from scholaros.services.service import Service


@dataclass(slots=True)
class ServiceDescriptor:
    """
    Holds registration specifications for a service in the service system.
    """

    name: str
    service_type: type[Service]
    instance: Service | None = None
    factory: Callable[..., Service] | None = None
    metadata: ServiceMetadata | None = None
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    diagnostics: ServiceDiagnostics = field(init=False)

    def __post_init__(self) -> None:
        if self.metadata is None and self.instance is not None:
            self.metadata = getattr(self.instance, "metadata", None)

        if self.metadata is not None and not self.dependencies:
            self.dependencies = self.metadata.dependencies

        self.diagnostics = ServiceDiagnostics(service_name=self.name)

    @property
    def is_instantiated(self) -> bool:
        """Return True if service instance exists."""
        return self.instance is not None


__all__ = [
    "ServiceDescriptor",
]
