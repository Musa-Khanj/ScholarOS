"""
ScholarOS
Kernel Service

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Base class for all ScholarOS services.

Responsibilities
----------------
• Bridge Component lifecycle
• Provide default lifecycle behavior
• Define the service contract
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from scholaros.core.base import (
    Component,
    ComponentMetadata,
    ComponentStatus,
)


class Service(Component, ABC):
    """
    Base class for all ScholarOS services.
    """

    def __init__(
        self,
        metadata: ComponentMetadata,
    ) -> None:
        """
        Initialize the service.
        """

        super().__init__(metadata)

    def initialize(
        self,
    ) -> None:
        """
        Initialize the service.
        """

        self._set_status(
            ComponentStatus.INITIALIZED,
        )

        self.start()

        self._set_status(
            ComponentStatus.RUNNING,
        )

    def shutdown(
        self,
    ) -> None:
        """
        Shut down the service.
        """

        self.stop()

        self._set_status(
            ComponentStatus.STOPPED,
        )

    def health(
        self,
    ) -> bool:
        """
        Return whether the service
        is healthy.
        """

        return (
            self.status
            is ComponentStatus.RUNNING
        )

    @abstractmethod
    def start(
        self,
    ) -> None:
        """
        Start the service.
        """

    @abstractmethod
    def stop(
        self,
    ) -> None:
        """
        Stop the service.
        """