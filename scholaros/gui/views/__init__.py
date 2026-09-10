"""
ScholarOS
GUI Views

Version : 1.0
Status  : In Development
Python  : 3.14+
"""

from __future__ import annotations

from scholaros.gui.views.chat import ChatPanel
from scholaros.gui.views.welcome import WelcomeView
from scholaros.gui.views.workspace_views import (
    ChatView,
    GUIView,
    HomeView,
    LibraryView,
    PluginsView,
    ResearchView,
    SettingsView,
)

__all__ = [
    "ChatPanel",
    "ChatView",
    "GUIView",
    "HomeView",
    "LibraryView",
    "PluginsView",
    "ResearchView",
    "SettingsView",
    "WelcomeView",
]