"""
ScholarOS
GUI Launcher

Version : 1.0
Status  : Stable
Python  : 3.14+
"""

from __future__ import annotations

from typing import Any

from scholaros.gui.builder import GUIBuilder


class GUILauncher:
    """
    Launches the ScholarOS GUI, wiring the production composition root.
    """

    def __init__(
        self,
        builder: GUIBuilder | None = None,
        services: Any | None = None,
        container: Any | None = None,
        use_mock_ai: bool = False,
    ) -> None:
        self._builder = builder if builder is not None else GUIBuilder()
        self._services = services
        self._container = container
        self._use_mock_ai = use_mock_ai

    @property
    def builder(
        self,
    ) -> GUIBuilder:
        """
        Return the configured builder.
        """
        return self._builder

    @property
    def services(self) -> Any | None:
        """Return injected services if provided."""
        return self._services

    @property
    def container(self) -> Any | None:
        """Return injected container if provided."""
        return self._container

    def launch(
        self,
    ) -> None:
        """
        Build and launch the GUI using the production composition root.
        """
        services = self._services
        container = self._container

        if services is None or container is None:
            from scholaros.bootstrap.runtime import bootstrap_runtime

            runtime = bootstrap_runtime(use_mock_ai=self._use_mock_ai)
            if services is None:
                services = runtime
            if container is None:
                container = runtime.container

        integration = self.builder.build(
            services=services,
            container=container,
        )

        integration.run()

    def __repr__(
        self,
    ) -> str:
        return f"{self.__class__.__name__}(builder={self.builder!r})"


def launch_gui(
    services: Any | None = None,
    container: Any | None = None,
    use_mock_ai: bool = False,
) -> None:
    """
    Convenience launcher for the GUI.
    """
    if services is not None or container is not None or use_mock_ai:
        GUILauncher(services=services, container=container, use_mock_ai=use_mock_ai).launch()
    else:
        GUILauncher().launch()


def main() -> None:
    """
    Command-line entrypoint to launch ScholarOS GUI.
    """
    launch_gui()
