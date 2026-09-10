from __future__ import annotations


class ApplicationLifecycle:
    """
    Application lifecycle manager.
    """

    def __init__(
        self,
        container,
    ) -> None:
        self.container = container

    def start(self) -> None:
        """
        Startup hook.
        """

    def stop(self) -> None:
        """
        Shutdown hook.
        """