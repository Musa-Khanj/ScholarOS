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


@pytest.fixture(autouse=True)
def clean_tk_after_each_test():
    """Cancel any pending Tk timer callbacks between tests to avoid cross-test interference."""
    yield
    default_root = getattr(tk, "_default_root", None)
    if default_root is not None:
        try:
            for timer_id in default_root.tk.call("after", "info"):
                try:
                    default_root.after_cancel(timer_id)
                except tk.TclError:
                    pass
            default_root.update_idletasks()
        except tk.TclError:
            pass
