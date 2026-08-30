"""
ScholarOS
GUI Main

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from __future__ import annotations

from typing import Any

from scholaros.gui.application import (
    GUIApplication,
)
from scholaros.ui.integration import (
    UIIntegration,
)


def create_application(
    integration: UIIntegration,
) -> GUIApplication:
    """
    Create a GUI application.
    """

    return GUIApplication(
        integration,
    )


def main(
    integration: UIIntegration,
) -> Any:
    """
    Start the GUI application.
    """

    application = create_application(
        integration,
    )

    return application.run()