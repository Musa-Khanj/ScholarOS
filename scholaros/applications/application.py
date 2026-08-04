from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scholaros.runtime import Runtime

class Application:
    """
    Represents a ScholarOS application.
    """

    def __init__(
        self,
        runtime: Runtime,
    ) -> None:
        """
        Initialize the application.
        """

        self._runtime = runtime

    @property
    def runtime(
        self,
    ) -> Runtime:
        """
        Return the configured runtime.
        """

        return self._runtime

    def run(
        self,
    ) -> object:
        """
        Execute the application.
        """

        return self._runtime.run()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the application.
        """

        return (
            f"{self.__class__.__name__}("
            f"runtime={self.runtime.__class__.__name__}"
            f")"
        )