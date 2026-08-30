"""
ScholarOS
GUI Components

Reusable GUI components used by the
ScholarOS desktop interface.
"""

from .chat_panel import ChatPanel
from .conversation_view import ConversationView
from .input_bar import InputBar
from .sidebar_button import SidebarButton
from .welcome_view import WelcomeView

__all__ = [
    "ChatPanel",
    "ConversationView",
    "InputBar",
    "SidebarButton",
    "WelcomeView",
]