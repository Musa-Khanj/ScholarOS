"""
ScholarOS Application Bootstrap.

High-level entry point coordinating logging initialization, runtime composition,
application lifecycle, and desktop shell execution.
"""

from __future__ import annotations

from typing import Any

from scholaros.bootstrap.lifecycle import ApplicationLifecycle
from scholaros.bootstrap.logging import configure_logging
from scholaros.bootstrap.runtime import RuntimeServices, bootstrap_runtime


class Bootstrap:
    """
    ScholarOS application bootstrap.
    """

    def __init__(
        self,
        runtime: RuntimeServices | None = None,
        use_mock_ai: bool = False,
        **runtime_kwargs: Any,
    ) -> None:
        configure_logging()

        self.runtime = runtime or bootstrap_runtime(use_mock_ai=use_mock_ai, **runtime_kwargs)
        self.configuration = self.runtime.config
        self.services = self.runtime
        self.container = self.runtime.container
        self.lifecycle = ApplicationLifecycle(self.container)

    def run(self) -> int:
        """
        Bootstrap and run ScholarOS desktop application.
        """
        self.lifecycle.start()
        try:
            from scholaros.gui.launcher import GUILauncher

            launcher = GUILauncher(
                services=self.runtime,
                container=self.container,
            )
            launcher.launch()
        finally:
            self.lifecycle.stop()

        return 0
