"""
ScholarOS
UI Integration Tests

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Integration tests for the ScholarOS UI integration
boundary.

These tests verify that the UI integration layer
correctly connects the application, presentation,
and frontend layers without bypassing the existing
ScholarOS architecture.
"""

from __future__ import annotations

from unittest.mock import Mock

from scholaros.ui.application import (
    UIApplication,
)
from scholaros.ui.frontend import (
    ScholarOSFrontend,
)
from scholaros.ui.integration import (
    UIIntegration,
)
from scholaros.ui.presentation import (
    UIPresentation,
)


def create_integration() -> UIIntegration:
    """
    Create a UI integration instance using
    mocked application dependencies.
    """

    application = Mock(
        spec=UIApplication,
    )

    application.status.return_value = (
        "READY"
    )

    application.info.return_value = {
        "research": True,
        "rag": True,
        "status": "READY",
    }

    return UIIntegration(
        application,
    )


def test_ui_integration_application_property():
    """
    Verify that the integration exposes the
    configured application.
    """

    application = Mock(
        spec=UIApplication,
    )

    integration = UIIntegration(
        application,
    )

    assert (
        integration.application
        is application
    )


def test_ui_integration_presentation_property():
    """
    Verify that the integration creates and
    exposes the presentation layer.
    """

    integration = create_integration()

    assert isinstance(
        integration.presentation,
        UIPresentation,
    )


def test_ui_integration_frontend_property():
    """
    Verify that the integration creates and
    exposes the frontend.
    """

    integration = create_integration()

    assert isinstance(
        integration.frontend,
        ScholarOSFrontend,
    )


def test_ui_integration_status():
    """
    Verify that status is delegated through
    the presentation layer.
    """

    integration = create_integration()

    assert (
        integration.status()
        == "READY"
    )


def test_ui_integration_info():
    """
    Verify that integration information
    contains all UI layers.
    """

    integration = create_integration()

    information = (
        integration.info()
    )

    assert (
        information["application"]
        is integration.application
    )

    assert (
        information["presentation"]
        is integration.presentation
    )

    assert (
        information["frontend"]
        is integration.frontend
    )

    assert (
        information["status"]
        == "READY"
    )


def test_ui_integration_frontend_uses_presentation():
    """
    Verify that the frontend is connected to
    the integration presentation layer.
    """

    integration = create_integration()

    assert (
        integration.frontend.presentation
        is integration.presentation
    )


def test_ui_integration_presentation_uses_application():
    """
    Verify that the presentation layer is
    connected to the integration application.
    """

    integration = create_integration()

    assert (
        integration.presentation.application
        is integration.application
    )


def test_ui_integration_refresh():
    """
    Verify that refresh delegates to the
    frontend.
    """

    integration = create_integration()

    integration.frontend.refresh = Mock()

    integration.refresh()

    integration.frontend.refresh.assert_called_once()


def test_ui_integration_run():
    """
    Verify that run delegates to the frontend.
    """

    integration = create_integration()

    integration.frontend.run = Mock(
        return_value="frontend-result",
    )

    result = integration.run()

    assert (
        result
        == "frontend-result"
    )

    integration.frontend.run.assert_called_once()


def test_ui_integration_repr():
    """
    Verify the developer-friendly
    representation of the integration.
    """

    integration = create_integration()

    representation = repr(
        integration,
    )

    assert (
        representation.startswith(
            "UIIntegration("
        )
    )

    assert (
        "application="
        in representation
    )

    assert (
        "presentation="
        in representation
    )

    assert (
        "frontend="
        in representation
    )


def test_ui_integration_preserves_application_identity():
    """
    Verify that the integration does not
    replace the configured application.
    """

    application = Mock(
        spec=UIApplication,
    )

    integration = UIIntegration(
        application,
    )

    assert (
        integration.application
        is application
    )

    assert (
        integration.presentation.application
        is application
    )


def test_ui_integration_layer_order():
    """
    Verify the intended UI layer order:

    Frontend
        ↓
    Presentation
        ↓
    Application
    """

    integration = create_integration()

    assert (
        integration.frontend.presentation
        is integration.presentation
    )

    assert (
        integration.presentation.application
        is integration.application
    )