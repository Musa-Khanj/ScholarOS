"""
ScholarOS
GUI Component Tests

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Unit tests for the GUIComponent base class.
"""

from __future__ import annotations

from scholaros.gui.component import (
    GUIComponent,
)


class DummyComponent(GUIComponent):
    """
    Concrete implementation used for testing.
    """

    def __init__(
        self,
        parent: object,
    ) -> None:
        super().__init__(
            parent,
        )

        self.built = False
        self.refreshed = False
        self.destroyed = False

    def build(
        self,
    ) -> None:
        self.built = True

    def refresh(
        self,
    ) -> None:
        self.refreshed = True

    def destroy(
        self,
    ) -> None:
        self.destroyed = True


def test_gui_component_parent_property():
    """
    Verify the parent property.
    """

    parent = object()

    component = DummyComponent(
        parent,
    )

    assert (
        component.parent
        is parent
    )


def test_gui_component_build():
    """
    Verify build().
    """

    component = DummyComponent(
        object(),
    )

    assert component.built is False

    component.build()

    assert component.built is True


def test_gui_component_refresh():
    """
    Verify refresh().
    """

    component = DummyComponent(
        object(),
    )

    assert component.refreshed is False

    component.refresh()

    assert component.refreshed is True


def test_gui_component_destroy():
    """
    Verify destroy().
    """

    component = DummyComponent(
        object(),
    )

    assert component.destroyed is False

    component.destroy()

    assert component.destroyed is True


def test_gui_component_repr():
    """
    Verify developer representation.
    """

    component = DummyComponent(
        object(),
    )

    representation = repr(
        component,
    )

    assert (
        representation.startswith(
            "DummyComponent("
        )
    )

    assert (
        "parent="
        in representation
    )