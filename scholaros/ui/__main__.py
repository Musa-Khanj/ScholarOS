"""
ScholarOS
UI Entry Point

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from scholaros.ui.application import (
    UIApplication,
)
from scholaros.ui.frontend import (
    main,
)
from scholaros.ui.presentation import (
    UIPresentation,
)


def create_application() -> UIApplication:
    """
    Create the default UI application.

    Domain pipelines are intentionally not
    constructed here. They must be supplied
    by the application's composition layer.
    """

    return UIApplication()


def run() -> None:
    """
    Start the ScholarOS UI.
    """

    application = create_application()

    presentation = UIPresentation(
        application,
    )

    main(
        presentation,
    )


if __name__ == "__main__":
    run()