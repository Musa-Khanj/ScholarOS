from __future__ import annotations

from scholaros.bootstrap.configuration import Configuration
from scholaros.bootstrap.container import ApplicationContainer
from scholaros.bootstrap.lifecycle import ApplicationLifecycle
from scholaros.bootstrap.logging import configure_logging


class Bootstrap:
    """
    ScholarOS application bootstrap.
    """

    def __init__(self) -> None:
        configure_logging()

        self.configuration = Configuration()

        self.container = ApplicationContainer(
            self.configuration,
        )

        self.lifecycle = ApplicationLifecycle(
            self.container,
        )

    def run(self) -> int:
        """
        Bootstrap and run ScholarOS.
        """

        self.lifecycle.start()

        try:
            self.container.ui.run()
        finally:
            self.lifecycle.stop()

        return 0