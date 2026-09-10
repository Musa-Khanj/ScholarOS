from __future__ import annotations

from scholaros.ui.__main__ import create_application
from scholaros.ui.integration import UIIntegration


class ApplicationContainer:
    """
    Dependency container.
    """

    def __init__(
        self,
        configuration,
    ) -> None:
        self.configuration = configuration

        application = create_application()

        self.ui = UIIntegration(
            application,
        )