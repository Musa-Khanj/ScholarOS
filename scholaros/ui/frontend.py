"""
ScholarOS
UI Frontend

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides the desktop frontend for ScholarOS.

The frontend is responsible only for user
interaction and presentation.

It delegates all application behavior to
UIPresentation and therefore does not access
Research, RAG, AI, Knowledge, or Kernel
subsystems directly.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from scholaros.ui.presentation import UIPresentation


class ScholarOSFrontend:
    """
    Provides the ScholarOS desktop frontend.

    The frontend delegates application
    operations to UIPresentation.
    """

    def __init__(
        self,
        presentation: UIPresentation,
        root: tk.Tk | None = None,
    ) -> None:
        """
        Initialize the ScholarOS frontend.

        Parameters
        ----------
        presentation:
            Configured UI presentation layer.

        root:
            Optional Tkinter root window.
        """

        self._presentation = presentation

        if root is not None:
            self._root = root

        else:
            existing_root = tk._default_root

            if existing_root is not None:
                try:
                    existing_root.winfo_exists()

                except tk.TclError:
                    existing_root = None

            if existing_root is not None:
                self._root = existing_root

            else:
                self._root = tk.Tk()

        self._status_var = tk.StringVar(
            master=self.root,
        )

        self._info_var = tk.StringVar(
            master=self.root,
        )

        self._rag_query_var = tk.StringVar(
            master=self.root,
        )

        self._rag_score_var = tk.StringVar(
            master=self.root,
            value="0.0",
        )

        self._research_template_var = (
            tk.StringVar(
                master=self.root,
            )
        )

        self._research_variables_var = (
            tk.StringVar(
                master=self.root,
            )
        )

        self._build_window()
        self._build_interface()
        self.refresh()

    @property
    def presentation(
        self,
    ) -> UIPresentation:
        """
        Return the UI presentation layer.
        """

        return self._presentation

    @property
    def root(
        self,
    ) -> tk.Tk:
        """
        Return the Tkinter root window.
        """

        return self._root

    def _build_window(
        self,
    ) -> None:
        """
        Configure the main application window.
        """

        self.root.title(
            "ScholarOS",
        )

        self.root.geometry(
            "1000x700",
        )

        self.root.minsize(
            800,
            550,
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.root.destroy,
        )

    def _build_interface(
        self,
    ) -> None:
        """
        Build the complete frontend interface.
        """

        self._build_header()
        self._build_body()
        self._build_status_bar()

    def _build_header(
        self,
    ) -> None:
        """
        Build the application header.
        """

        header = ttk.Frame(
            self.root,
            padding=16,
        )

        header.pack(
            fill="x",
        )

        title = ttk.Label(
            header,
            text="ScholarOS",
            font=(
                "TkDefaultFont",
                20,
                "bold",
            ),
        )

        title.pack(
            anchor="w",
        )

        subtitle = ttk.Label(
            header,
            text=(
                "AI Research Operating System"
            ),
        )

        subtitle.pack(
            anchor="w",
            pady=(2, 0),
        )

    def _build_body(
        self,
    ) -> None:
        """
        Build the main notebook interface.
        """

        notebook = ttk.Notebook(
            self.root,
        )

        notebook.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 16),
        )

        self._build_dashboard_tab(
            notebook,
        )

        self._build_rag_tab(
            notebook,
        )

        self._build_research_tab(
            notebook,
        )

    def _build_dashboard_tab(
        self,
        notebook: ttk.Notebook,
    ) -> None:
        """
        Build the dashboard tab.
        """

        frame = ttk.Frame(
            notebook,
            padding=20,
        )

        notebook.add(
            frame,
            text="Dashboard",
        )

        ttk.Label(
            frame,
            text="System Status",
            font=(
                "TkDefaultFont",
                14,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 10),
        )

        ttk.Label(
            frame,
            textvariable=self._status_var,
        ).pack(
            anchor="w",
            pady=(0, 20),
        )

        ttk.Label(
            frame,
            text="System Information",
            font=(
                "TkDefaultFont",
                14,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 10),
        )

        ttk.Label(
            frame,
            textvariable=self._info_var,
            justify="left",
        ).pack(
            anchor="w",
        )

        ttk.Button(
            frame,
            text="Refresh",
            command=self.refresh,
        ).pack(
            anchor="w",
            pady=(25, 0),
        )

    def _build_rag_tab(
        self,
        notebook: ttk.Notebook,
    ) -> None:
        """
        Build the RAG query tab.
        """

        frame = ttk.Frame(
            notebook,
            padding=20,
        )

        notebook.add(
            frame,
            text="RAG",
        )

        ttk.Label(
            frame,
            text="Knowledge Query",
            font=(
                "TkDefaultFont",
                14,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 10),
        )

        ttk.Label(
            frame,
            text="Question",
        ).pack(
            anchor="w",
        )

        ttk.Entry(
            frame,
            textvariable=self._rag_query_var,
        ).pack(
            fill="x",
            pady=(4, 12),
        )

        ttk.Label(
            frame,
            text="Minimum Score",
        ).pack(
            anchor="w",
        )

        ttk.Entry(
            frame,
            textvariable=self._rag_score_var,
        ).pack(
            fill="x",
            pady=(4, 12),
        )

        ttk.Button(
            frame,
            text="Run RAG Query",
            command=self.run_rag,
        ).pack(
            anchor="w",
        )

        ttk.Label(
            frame,
            text="Response",
            font=(
                "TkDefaultFont",
                12,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(20, 5),
        )

        self._rag_output = tk.Text(
            frame,
            wrap="word",
            height=18,
        )

        self._rag_output.pack(
            fill="both",
            expand=True,
        )

    def _build_research_tab(
        self,
        notebook: ttk.Notebook,
    ) -> None:
        """
        Build the research tab.
        """

        frame = ttk.Frame(
            notebook,
            padding=20,
        )

        notebook.add(
            frame,
            text="Research",
        )

        ttk.Label(
            frame,
            text="Research Template",
            font=(
                "TkDefaultFont",
                14,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 10),
        )

        ttk.Label(
            frame,
            text="Template",
        ).pack(
            anchor="w",
        )

        ttk.Entry(
            frame,
            textvariable=(
                self._research_template_var
            ),
        ).pack(
            fill="x",
            pady=(4, 12),
        )

        ttk.Label(
            frame,
            text=(
                "Variables "
                "(optional, e.g. topic=AI)"
            ),
        ).pack(
            anchor="w",
        )

        ttk.Entry(
            frame,
            textvariable=(
                self._research_variables_var
            ),
        ).pack(
            fill="x",
            pady=(4, 12),
        )

        button_frame = ttk.Frame(
            frame,
        )

        button_frame.pack(
            fill="x",
            pady=(0, 15),
        )

        ttk.Button(
            button_frame,
            text="Build Prompt",
            command=self.build_research,
        ).pack(
            side="left",
        )

        ttk.Button(
            button_frame,
            text="Execute Research",
            command=self.execute_research,
        ).pack(
            side="left",
            padx=(10, 0),
        )

        ttk.Label(
            frame,
            text="Result",
            font=(
                "TkDefaultFont",
                12,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(5, 5),
        )

        self._research_output = tk.Text(
            frame,
            wrap="word",
            height=18,
        )

        self._research_output.pack(
            fill="both",
            expand=True,
        )

    def _build_status_bar(
        self,
    ) -> None:
        """
        Build the bottom status bar.
        """

        frame = ttk.Frame(
            self.root,
            padding=8,
        )

        frame.pack(
            fill="x",
        )

        self._status_bar = ttk.Label(
            frame,
            text="ScholarOS",
            anchor="w",
        )

        self._status_bar.pack(
            fill="x",
        )

    def refresh(
        self,
    ) -> None:
        """
        Refresh dashboard information.
        """

        try:
            self._status_var.set(
                self.presentation.render_status(),
            )

            self._info_var.set(
                self.presentation.render_info(),
            )

            self._status_bar.configure(
                text=self.presentation.status(),
            )

        except Exception as exc:
            self._status_var.set(
                "ScholarOS status: ERROR",
            )

            self._info_var.set(
                f"Unable to load status: {exc}",
            )

            self._status_bar.configure(
                text="ERROR",
            )

    def run_rag(
        self,
    ) -> None:
        """
        Execute the RAG query entered by
        the user.
        """

        query = (
            self._rag_query_var
            .get()
            .strip()
        )

        if not query:
            messagebox.showwarning(
                "ScholarOS",
                "Please enter a question.",
            )

            return

        try:
            minimum_score = float(
                self._rag_score_var.get(),
            )

        except ValueError:
            messagebox.showerror(
                "ScholarOS",
                "Minimum score must be a number.",
            )

            return

        try:
            response = (
                self.presentation.rag_query(
                    query,
                    minimum_score,
                )
            )

            self._set_text(
                self._rag_output,
                self._format_result(
                    response,
                ),
            )

            self._status_bar.configure(
                text="RAG query completed.",
            )

        except Exception as exc:
            self._set_text(
                self._rag_output,
                f"RAG query failed:\n{exc}",
            )

            self._status_bar.configure(
                text="RAG query failed.",
            )

    def build_research(
        self,
    ) -> None:
        """
        Build a research prompt without
        executing it.
        """

        template = (
            self._research_template_var
            .get()
            .strip()
        )

        if not template:
            messagebox.showwarning(
                "ScholarOS",
                "Please enter a research template.",
            )

            return

        try:
            variables = self._parse_variables()

        except ValueError as exc:
            self._set_text(
                self._research_output,
                f"Research variables failed:\n{exc}",
            )

            self._status_bar.configure(
                text="Research variables invalid.",
            )

            return

        try:
            result = (
                self.presentation.research_build(
                    template,
                    **variables,
                )
            )

            self._set_text(
                self._research_output,
                result,
            )

            self._status_bar.configure(
                text="Research prompt built.",
            )

        except Exception as exc:
            self._set_text(
                self._research_output,
                f"Research build failed:\n{exc}",
            )

            self._status_bar.configure(
                text="Research build failed.",
            )

    def execute_research(
        self,
    ) -> None:
        """
        Execute the configured research
        operation.
        """

        template = (
            self._research_template_var
            .get()
            .strip()
        )

        if not template:
            messagebox.showwarning(
                "ScholarOS",
                "Please enter a research template.",
            )

            return

        try:
            variables = self._parse_variables()

        except ValueError as exc:
            self._set_text(
                self._research_output,
                f"Research variables failed:\n{exc}",
            )

            self._status_bar.configure(
                text="Research variables invalid.",
            )

            return

        try:
            result = (
                self.presentation.research_execute(
                    template,
                    **variables,
                )
            )

            self._set_text(
                self._research_output,
                self._format_result(
                    result,
                ),
            )

            self._status_bar.configure(
                text="Research execution completed.",
            )

        except Exception as exc:
            self._set_text(
                self._research_output,
                f"Research execution failed:\n{exc}",
            )

            self._status_bar.configure(
                text="Research execution failed.",
            )

    def _parse_variables(
        self,
    ) -> dict[str, str]:
        """
        Parse comma-separated research
        variables.
        """

        raw = (
            self._research_variables_var
            .get()
            .strip()
        )

        if not raw:
            return {}

        variables: dict[str, str] = {}

        for item in raw.split(","):
            item = item.strip()

            if not item:
                continue

            if "=" not in item:
                raise ValueError(
                    "Research variables must use "
                    "the format name=value."
                )

            name, value = item.split(
                "=",
                1,
            )

            name = name.strip()
            value = value.strip()

            if not name:
                raise ValueError(
                    "Research variable name "
                    "cannot be empty."
                )

            variables[name] = value

        return variables

    @staticmethod
    def _set_text(
        widget: tk.Text,
        value: object,
    ) -> None:
        """
        Replace the contents of a text widget.
        """

        widget.delete(
            "1.0",
            tk.END,
        )

        widget.insert(
            tk.END,
            str(value),
        )

    @staticmethod
    def _format_result(
        result: object,
    ) -> str:
        """
        Convert a ScholarOS result into
        presentation-ready text.
        """

        if result is None:
            return ""

        content = getattr(
            result,
            "content",
            None,
        )

        if isinstance(
            content,
            str,
        ):
            return content

        return str(result)

    def run(
        self,
    ) -> None:
        """
        Start the frontend event loop.
        """

        self.root.mainloop()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the frontend.
        """

        return (
            f"{self.__class__.__name__}("
            f"presentation={self.presentation!r}"
            f")"
        )


def create_frontend(
    presentation: UIPresentation,
) -> ScholarOSFrontend:
    """
    Create a ScholarOS frontend from an
    existing presentation layer.
    """

    return ScholarOSFrontend(
        presentation,
    )


def main(
    presentation: UIPresentation,
) -> None:
    """
    Start the ScholarOS frontend.
    """

    frontend = create_frontend(
        presentation,
    )

    frontend.run()