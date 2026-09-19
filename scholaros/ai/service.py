"""
ScholarOS AI Service.

Bridges the AI subsystem with the ScholarOS Service Framework and
Dependency Injection Container.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scholaros.ai.client import AIClient
from scholaros.ai.factory import AIFactory
from scholaros.ai.manager import AIManager
from scholaros.ai.registry import ProviderRegistry
from scholaros.services.health import HealthStatus, ServiceHealth
from scholaros.services.metadata import ServiceMetadata
from scholaros.services.service import Service

if TYPE_CHECKING:
    from scholaros.ai.prompt_session import PromptSession
    from scholaros.container.container import Container


class AIService(Service):
    """
    Core AI subsystem service for ScholarOS.
    """

    def __init__(
        self,
        session: PromptSession | None = None,
        manager: AIManager | None = None,
        metadata: ServiceMetadata | None = None,
    ) -> None:
        if metadata is None:
            metadata = ServiceMetadata(
                name="AIService",
                version="1.0.0",
                description="ScholarOS Core AI Service",
                capabilities=("generation", "streaming", "embeddings", "model_routing"),
                tags=("ai", "core"),
            )
        super().__init__(metadata=metadata)

        self._session = session
        self._manager = manager or AIFactory.create_manager()
        self.client = AIClient(self._manager)

    @property
    def manager(self) -> AIManager:
        """Return the underlying AIManager."""
        return self._manager

    @property
    def session(self) -> PromptSession:
        """Return the legacy PromptSession if configured."""
        if self._session is None:
            raise AttributeError("AIService was initialized without a PromptSession.")
        return self._session

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute a prompt template or model call.
        """
        if self._session is not None and args and isinstance(args[0], str):
            return self._session.execute(args[0], **kwargs)
        if "template" in kwargs and self._session is not None:
            return self._session.execute(**kwargs)
        return None

    def build(self, template: str, **variables: str) -> str:
        """Build prompt template without executing."""
        if self._session is None:
            raise AttributeError("AIService was initialized without a PromptSession.")
        return self._session.build(template, **variables)

    def contains(self, template: str) -> bool:
        """Return True if prompt template exists."""
        if self._session is None:
            return False
        return self._session.builder.contains(template)

    # ---------------------------------------------------------
    # Lifecycle Hooks
    # ---------------------------------------------------------

    def initialize(self) -> None:
        super().initialize()

    def start(self) -> None:
        super().start()

    def stop(self) -> None:
        super().stop()

    def shutdown(self) -> None:
        super().shutdown()

    def health(self) -> ServiceHealth:
        """Report overall health of the AI subsystem."""
        if not self.is_running():
            return ServiceHealth(
                service_name=self.name,
                status=HealthStatus.UNKNOWN,
                details=f"Service in state: {self.status.name}",
            )
        return self._manager.health()

    # ---------------------------------------------------------
    # DI Container Integration
    # ---------------------------------------------------------

    def register_container(self, container: Container) -> None:
        """
        Register AI components into the Dependency Injection container.
        """
        container.add_instance(AIService, self)
        container.add_instance(AIManager, self._manager)
        container.add_instance(AIClient, self.client)
        container.add_instance(ProviderRegistry, self._manager.registry)

    @classmethod
    def configure_container(
        cls,
        container: Container,
        manager: AIManager | None = None,
    ) -> AIService:
        """
        Convenience factory to create AIService and wire it into Container.
        """
        service = cls(manager=manager)
        service.register_container(container)
        return service

    def __repr__(self) -> str:
        if self._session is not None:
            return f"{self.__class__.__name__}(session={self._session!r})"
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"enabled={self.enabled!r}"
            f")"
        )


__all__ = [
    "AIService",
]
