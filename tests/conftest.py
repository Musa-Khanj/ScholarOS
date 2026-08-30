"""
ScholarOS
Pytest Configuration

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Global test fixtures and Tkinter safety patches.
"""

import tkinter as tk
from importlib import import_module

# Load pytest dynamically so editors do not report an unresolved static import
# when the test environment's interpreter is not selected.
pytest = import_module("pytest")


@pytest.fixture(scope="session", autouse=True)
def manage_tk_root():
    """
    Prevents multiple Tcl interpreters from being created and destroyed.
    
    On Windows, creating a new tk.Tk() after destroying a previous one
    in the same process causes 'Can't find a usable init.tcl' errors.
    This patch intercepts destroy() calls during tests, keeping the
    interpreter alive but hiding the window and clearing its children.
    """
    original_destroy = tk.Tk.destroy

    def safe_destroy(self):
        try:
            self.withdraw()
            for child in list(self.children.values()):
                child.destroy()
        except tk.TclError:
            pass

    tk.Tk.destroy = safe_destroy

    yield

    # Restore original destroy and clean up at the end of the test session
    tk.Tk.destroy = original_destroy
    if tk._default_root is not None:
        try:
            original_destroy(tk._default_root)
        except tk.TclError:
            pass