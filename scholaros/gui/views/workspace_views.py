"""
ScholarOS GUI Workspace Views.

Provides specialized workspace views for the ScholarOS shell:
- HomeView: System overview, status, and quick-action navigation.
- ChatView: Conversational AI interface with provider/model routing and history.
- ResearchView: Deep research execution, synthesis viewing, and provenance.
- LibraryView: Knowledge retrieval and document search viewer.
- PluginsView: Plugin manager interface for inspection and toggling.
- SettingsView: System configuration, provider selection, and subsystem telemetry.
"""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from scholaros.gui.chat import GUIChat


class GUIView:
    """
    Base workspace view providing layout frames and headers.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str = "",
        description: str = "",
        name: str = "",
        application: Any | None = None,
    ) -> None:
        self._parent = parent
        self._name = name or title.lower()
        self._built = False
        self._application = application

        self._frame = ttk.Frame(
            parent,
            padding=20,
        )

        if title:
            ttk.Label(
                self._frame,
                text=title,
                font=(
                    "TkDefaultFont",
                    18,
                    "bold",
                ),
            ).pack(
                anchor="w",
                pady=(0, 6),
            )

        if description:
            ttk.Label(
                self._frame,
                text=description,
                justify="left",
            ).pack(
                anchor="w",
                pady=(0, 12),
            )

    @property
    def name(self) -> str:
        return self._name

    @property
    def built(self) -> bool:
        return self._built

    @property
    def frame(self) -> ttk.Frame:
        return self._frame

    @property
    def application(self) -> Any | None:
        return self._application

    def set_application(self, application: Any) -> None:
        self._application = application

    def show(self) -> None:
        """Bring view frame to top."""
        if hasattr(self.frame, "tkraise"):
            self.frame.tkraise()


class HomeView(GUIView):
    """
    Welcome and summary landing view.
    """

    def __init__(
        self,
        parent: tk.Widget,
        application: Any | None = None,
        on_navigate: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(
            parent,
            title="ScholarOS Home",
            description="Autonomous Research Operating System",
            name="home",
            application=application,
        )
        self.on_navigate = on_navigate

        # Quick Actions
        actions_frame = ttk.LabelFrame(self.frame, text="Quick Actions", padding=12)
        actions_frame.pack(fill="x", pady=(0, 16))

        ttk.Button(
            actions_frame,
            text="💬 Start AI Chat",
            command=lambda: self._navigate("chat"),
        ).pack(side="left", padx=6, pady=4)

        ttk.Button(
            actions_frame,
            text="📄 Run Research",
            command=lambda: self._navigate("research"),
        ).pack(side="left", padx=6, pady=4)

        ttk.Button(
            actions_frame,
            text="📚 Search Knowledge Library",
            command=lambda: self._navigate("library"),
        ).pack(side="left", padx=6, pady=4)

        ttk.Button(
            actions_frame,
            text="⚙ Settings & Models",
            command=lambda: self._navigate("settings"),
        ).pack(side="left", padx=6, pady=4)

        # Status Summary
        self._info_label = ttk.Label(
            self.frame,
            text="System Status: Ready. Connect to AI models and research pipelines above.",
            font=("TkDefaultFont", 10),
        )
        self._info_label.pack(anchor="w", pady=8)
        self._built = True

    def _navigate(self, target: str) -> None:
        if self.on_navigate:
            self.on_navigate(target)

    def refresh(self) -> None:
        if self.application:
            info = self.application.info()
            status_text = f"Status: {info.get('status', 'READY')} | AI: {'Yes' if info.get('ai') else 'No'} | RAG: {'Yes' if info.get('rag') else 'No'}"
            self._info_label.configure(text=status_text)


class ChatView:
    """
    Interactive Chat workspace view with conversation log and prompt input.
    """

    def __init__(
        self,
        parent: tk.Widget,
        application: Any | None = None,
    ) -> None:
        self._parent = parent
        self._application = application
        self._chat = GUIChat(parent)
        self._chat.build()
        self._is_generating: bool = False

        # Hook send button
        if self._chat.send_button is not None:
            self._chat.send_button.configure(command=self._on_send_clicked)

    @property
    def frame(self) -> ttk.Frame:
        return self._chat.frame

    @property
    def chat(self) -> GUIChat:
        return self._chat

    @property
    def application(self) -> Any | None:
        return self._application

    @property
    def is_generating(self) -> bool:
        return self._is_generating

    @property
    def session(self) -> Any | None:
        if self._application is not None and hasattr(self._application, "session"):
            return self._application.session
        return None

    @property
    def conversation(self) -> Any | None:
        if self._application is not None and hasattr(self._application, "conversation"):
            return self._application.conversation
        return None

    def set_application(self, application: Any) -> None:
        self._application = application

    def show(self) -> None:
        if hasattr(self.frame, "tkraise"):
            self.frame.tkraise()

    def _on_send_clicked(self) -> None:
        """Handle send button or Enter key: dispatch async if supported, else sync."""
        if self._application is not None and hasattr(self._application, "chat_async"):
            self.send_message_async()
        else:
            self.send_message()

    def send_message(self, prompt_text: str | None = None) -> str | None:
        """
        Send a user message, invoke application.chat(), and display the response.
        """
        if prompt_text is not None:
            prompt = prompt_text.strip()
        elif self._chat.input is not None:
            prompt = self._chat.input.get("1.0", "end").strip()
        else:
            prompt = ""

        if not prompt:
            return None

        # Display user message
        self._chat.append_message("You", prompt)
        if self._chat.input is not None:
            self._chat.input.delete("1.0", "end")

        if self.application is not None:
            try:
                response = self.application.chat(prompt)
                raw_cites = getattr(self.application, "last_citations", None)
                citations = raw_cites if isinstance(raw_cites, (list, tuple)) else None
                self._chat.append_message("ScholarOS", response, citations=citations)
                return response
            except Exception as exc:
                err_msg = f"Error: {exc}"
                self._chat.append_message("System", err_msg)
                if hasattr(self.application, "set_status"):
                    self.application.set_status(err_msg, error=True)
                return None
        else:
            reply = f"Echo: {prompt} (Offline mode)"
            self._chat.append_message("ScholarOS", reply)
            return reply

    def send_message_async(
        self,
        prompt_text: str | None = None,
        on_complete: Any | None = None,
        on_error: Any | None = None,
    ) -> None:
        """
        Send a user message asynchronously via application.chat_async() keeping GUI responsive.
        """
        if prompt_text is not None:
            prompt = prompt_text.strip()
        elif self._chat.input is not None:
            prompt = self._chat.input.get("1.0", "end").strip()
        else:
            prompt = ""

        if not prompt or self._is_generating:
            return

        self._is_generating = True
        self._chat.append_message("You", prompt)
        if self._chat.input is not None:
            self._chat.input.delete("1.0", "end")

        # Disable send button during generation
        if self._chat.send_button is not None:
            self._chat.send_button.configure(state="disabled")

        if self._application is not None and hasattr(self._application, "set_status"):
            self._application.set_status("Thinking...")

        def _handle_success(response: str) -> None:
            self._is_generating = False
            if self._chat.send_button is not None:
                self._chat.send_button.configure(state="normal")
            raw_cites = getattr(self._application, "last_citations", None)
            citations = raw_cites if isinstance(raw_cites, (list, tuple)) else None
            self._chat.append_message("ScholarOS", response, citations=citations)
            if self._application is not None and hasattr(self._application, "set_status"):
                self._application.set_status("Ready")
            if on_complete:
                on_complete(response)

        def _handle_error(exc: Exception) -> None:
            self._is_generating = False
            if self._chat.send_button is not None:
                self._chat.send_button.configure(state="normal")
            err_msg = f"Error: {exc}"
            self._chat.append_message("System", err_msg)
            if self._application is not None and hasattr(self._application, "set_status"):
                self._application.set_status(err_msg, error=True)
            if on_error:
                on_error(exc)

        if self._application is not None and hasattr(self._application, "chat_async"):
            self._application.chat_async(
                prompt,
                on_complete=_handle_success,
                on_error=_handle_error,
            )
        else:
            try:
                if self._application is not None:
                    res = self._application.chat(prompt)
                else:
                    res = f"Echo: {prompt} (Offline mode)"
                _handle_success(res)
            except Exception as e:
                _handle_error(e)

    def clear(self) -> None:
        self._chat.clear()
        if self._application is not None and hasattr(self._application, "clear_chat"):
            self._application.clear_chat()


class ResearchView(GUIView):
    """
    Research workspace for running queries, multi-stage workflows, and reviewing findings.
    """

    def __init__(
        self,
        parent: tk.Widget,
        application: Any | None = None,
    ) -> None:
        super().__init__(
            parent,
            title="Research Workspace",
            description="Formulate hypotheses, execute deep research tasks, and review citations.",
            name="research",
            application=application,
        )

        self._state: str = "idle"
        self._last_result: Any | None = None
        self._stage_subscription: Any | None = None

        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill="x", pady=(0, 6))

        ttk.Label(input_frame, text="Topic / Query:").pack(side="left", padx=(0, 8))
        self._entry = ttk.Entry(input_frame)
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._entry.bind("<Return>", lambda e: self._on_run_clicked())

        self._run_btn = ttk.Button(
            input_frame,
            text="Run Research",
            command=self._on_run_clicked,
        )
        self._run_btn.pack(side="left", padx=(0, 4))

        self._cancel_btn = ttk.Button(
            input_frame,
            text="Cancel",
            state="disabled",
            command=self.cancel_research,
        )
        self._cancel_btn.pack(side="left")

        # Stage and progress telemetry header
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill="x", pady=(0, 8))

        self._stage_label = ttk.Label(
            status_frame,
            text="Status: Ready",
            font=("TkDefaultFont", 9),
            foreground="#6c757d",
        )
        self._stage_label.pack(side="left")

        # Results area
        results_frame = ttk.LabelFrame(self.frame, text="Research Results & Citations", padding=10)
        results_frame.pack(fill="both", expand=True)

        self._results_text = tk.Text(results_frame, wrap="word", height=12)
        self._results_text.pack(fill="both", expand=True)

        # Style tags
        self._results_text.tag_configure(
            "section_header", font=("TkDefaultFont", 10, "bold"), foreground="#0d6efd"
        )
        self._results_text.tag_configure("findings", font=("TkDefaultFont", 10))
        self._results_text.tag_configure(
            "citations", font=("TkDefaultFont", 9, "italic"), foreground="#495057"
        )
        self._results_text.tag_configure("meta", font=("TkDefaultFont", 9), foreground="#6c757d")
        self._results_text.tag_configure(
            "error", font=("TkDefaultFont", 10, "bold"), foreground="#dc3545"
        )
        self._results_text.tag_configure(
            "cancelled", font=("TkDefaultFont", 10, "bold"), foreground="#fd7e14"
        )

        self._results_text.insert("1.0", "Enter a topic above and click 'Run Research'.\n")
        self._results_text.configure(state="disabled")

        self._built = True
        self._setup_event_listeners()

    @property
    def state(self) -> str:
        """Return current execution state: idle, running, completed, failed, cancelled."""
        return self._state

    @property
    def is_running(self) -> bool:
        """Return True if research is actively running."""
        return self._state == "running"

    @property
    def last_result(self) -> Any | None:
        """Return the result from the most recent research execution."""
        return self._last_result

    @property
    def results_text(self) -> tk.Text:
        return self._results_text

    @property
    def run_button(self) -> ttk.Button:
        return self._run_btn

    @property
    def cancel_button(self) -> ttk.Button:
        return self._cancel_btn

    @property
    def stage_label(self) -> ttk.Label:
        return self._stage_label

    def set_application(self, application: Any) -> None:
        super().set_application(application)
        self._setup_event_listeners()

    def _setup_event_listeners(self) -> None:
        if self._application is not None and hasattr(self._application, "event_bus"):
            bus = self._application.event_bus
            if bus is not None and hasattr(bus, "subscribe"):
                try:
                    self._stage_subscription = bus.subscribe(
                        "ResearchStageStarted",
                        self._on_stage_started,
                    )
                except Exception:
                    pass

    def _on_stage_started(self, event: Any) -> None:
        """Handle ResearchStageStarted event from EventBus to update stage indicator in real-time."""
        stage_name = None
        if hasattr(event, "payload") and isinstance(event.payload, dict):
            stage_name = event.payload.get("stage")
        elif hasattr(event, "stage"):
            stage_name = event.stage

        if stage_name and self._state == "running":
            stage_display = f"Stage: {stage_name.capitalize()}..."
            self._update_stage_ui(stage_display)

    def _update_stage_ui(self, text: str) -> None:
        """Safely update stage label on main thread."""
        try:
            self._stage_label.configure(text=text)
        except Exception:
            pass

    def _on_run_clicked(self) -> None:
        """Handle Run Research button click: use async if available, else sync."""
        if self.is_running:
            return
        if self._application is not None and hasattr(self._application, "research_async"):
            self.run_research_async()
        else:
            self.run_research()

    def cancel_research(self, reason: str = "User requested cancellation") -> bool:
        """Request cancellation of currently running research task."""
        if not self.is_running:
            return False
        self._update_stage_ui("Cancelling research...")
        if self._application is not None and hasattr(self._application, "cancel_research"):
            return bool(self._application.cancel_research(reason=reason))
        return False

    def run_research(self, topic: str | None = None, use_workflow: bool = False) -> Any:
        """
        Execute research synchronously and display results.
        """
        if self.is_running:
            return None

        query = topic or self._entry.get().strip()
        if not query:
            return None

        self._state = "running"
        self._run_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")
        self._update_stage_ui("Running research...")

        self._results_text.configure(state="normal")
        self._results_text.delete("1.0", "end")
        self._results_text.insert("end", f"Executing research on: {query}...\n\n")
        self._results_text.configure(state="disabled")

        if self.application is not None:
            try:
                if use_workflow:
                    result = self.application.research(query, use_workflow=True)
                else:
                    result = self.application.research(query)

                self._render_result(result)
                if self._check_is_cancelled(result):
                    self._state = "cancelled"
                    self._update_stage_ui("Status: Cancelled")
                else:
                    self._state = "completed"
                    self._update_stage_ui("Status: Completed")
                return result
            except Exception as exc:
                self._state = "failed"
                self._update_stage_ui("Status: Failed")
                self._results_text.configure(state="normal")
                self._results_text.insert("end", f"Error during research: {exc}\n", "error")
                self._results_text.configure(state="disabled")
                if hasattr(self.application, "set_status"):
                    self.application.set_status(str(exc), error=True)
                return None
            finally:
                self._run_btn.configure(state="normal")
                self._cancel_btn.configure(state="disabled")
        else:
            simulated = f"Research results for {query}"
            self._render_result(simulated)
            self._state = "completed"
            self._update_stage_ui("Status: Completed (Offline)")
            self._run_btn.configure(state="normal")
            self._cancel_btn.configure(state="disabled")
            return simulated

    def run_research_async(
        self,
        topic: str | None = None,
        use_workflow: bool = False,
        on_complete: Any | None = None,
        on_error: Any | None = None,
        on_progress: Any | None = None,
    ) -> None:
        """
        Execute research asynchronously via application.research_async() keeping UI responsive.
        """
        if self.is_running:
            return

        query = topic or self._entry.get().strip()
        if not query:
            return

        self._state = "running"
        self._run_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")
        self._update_stage_ui("Starting research...")

        self._results_text.configure(state="normal")
        self._results_text.delete("1.0", "end")
        self._results_text.insert("end", f"Executing research on: {query}...\n\n")
        self._results_text.configure(state="disabled")

        if self._application is not None and hasattr(self._application, "set_status"):
            self._application.set_status("Researching...")

        def _handle_success(result: Any) -> None:
            self._run_btn.configure(state="normal")
            self._cancel_btn.configure(state="disabled")

            if self._check_is_cancelled(result):
                self._state = "cancelled"
                self._update_stage_ui("Status: Cancelled")
                if self._application is not None and hasattr(self._application, "set_status"):
                    self._application.set_status("Research cancelled.")
            else:
                self._state = "completed"
                self._update_stage_ui("Status: Completed")
                if self._application is not None and hasattr(self._application, "set_status"):
                    self._application.set_status("Ready")

            self._render_result(result)
            if on_complete:
                on_complete(result)

        def _handle_error(exc: Exception) -> None:
            self._state = "failed"
            self._run_btn.configure(state="normal")
            self._cancel_btn.configure(state="disabled")
            self._update_stage_ui("Status: Failed")

            self._results_text.configure(state="normal")
            self._results_text.insert("end", f"Error during research: {exc}\n", "error")
            self._results_text.configure(state="disabled")

            if self._application is not None and hasattr(self._application, "set_status"):
                self._application.set_status(f"Error: {exc}", error=True)

            if on_error:
                on_error(exc)

        if self._application is not None and hasattr(self._application, "research_async"):
            self._application.research_async(
                query,
                use_workflow=use_workflow,
                on_complete=_handle_success,
                on_error=_handle_error,
            )
        else:
            try:
                if self.application is not None:
                    res = self.application.research(query, use_workflow=use_workflow)
                else:
                    res = f"Research results for {query}"
                _handle_success(res)
            except Exception as e:
                _handle_error(e)

    def _check_is_cancelled(self, result: Any) -> bool:
        """Helper to determine if a result was cancelled."""
        if getattr(result, "is_cancelled", False):
            return True
        if hasattr(result, "workflow_context") and result.workflow_context is not None:
            if getattr(result.workflow_context, "is_cancelled", False):
                return True
        if hasattr(result, "response") and hasattr(result.response, "metadata"):
            if isinstance(result.response.metadata, dict) and result.response.metadata.get(
                "cancelled"
            ):
                return True
        content = getattr(result, "content", str(result))
        return "[Workflow Cancelled]" in str(content)

    def _render_result(self, result: Any) -> None:
        """Display ResearchResult findings, citations, workflow stages, and telemetry."""
        self._last_result = result
        self._results_text.configure(state="normal")
        self._results_text.delete("1.0", "end")

        is_cancelled = self._check_is_cancelled(result)

        if is_cancelled:
            self._results_text.insert("end", "⚠️ [Research Cancelled]\n\n", "cancelled")
            content = getattr(result, "content", str(result))
            self._results_text.insert("end", f"{content}\n", "findings")
            self._results_text.configure(state="disabled")
            return

        # 1. Findings / Content
        answer = getattr(result, "content", getattr(result, "answer", str(result)))
        self._results_text.insert("end", "Findings:\n", "section_header")
        self._results_text.insert("end", f"{answer}\n\n", "findings")

        # 2. Citations & Bibliography
        citations_rendered = False
        report = getattr(result, "report", None)
        if report is not None and hasattr(report, "citations") and report.citations:
            self._results_text.insert("end", "📚 Citations & Sources:\n", "section_header")
            for i, cite in enumerate(report.citations, 1):
                title = getattr(cite, "title", str(cite))
                source = getattr(cite, "source", "ScholarOS Knowledge Base")
                url = getattr(cite, "url", None)
                url_str = f" ({url})" if url else ""
                self._results_text.insert(
                    "end", f"  [{i}] {title} — {source}{url_str}\n", "citations"
                )
            self._results_text.insert("end", "\n")
            citations_rendered = True

        raw_sources = getattr(result, "sources", None)
        if not citations_rendered and raw_sources:
            sources_list = list(raw_sources)
            if sources_list:
                self._results_text.insert("end", "📚 Sources:\n", "section_header")
                for i, src in enumerate(sources_list, 1):
                    self._results_text.insert("end", f"  [{i}] {src}\n", "citations")
                self._results_text.insert("end", "\n")

        # 3. Workflow Stages Summary
        has_wf = getattr(result, "has_workflow", False)
        steps = getattr(result, "steps", None)
        if has_wf and steps:
            self._results_text.insert("end", "⏱️ Workflow Stages:\n", "section_header")
            for s in steps:
                s_name = getattr(s, "name", "step").capitalize()
                s_dur = getattr(s, "duration_ms", 0.0)
                status_name = (
                    getattr(s.status, "name", str(s.status)).lower()
                    if hasattr(s, "status")
                    else "done"
                )
                self._results_text.insert(
                    "end", f"  • {s_name}: {status_name} ({s_dur:.1f}ms)\n", "meta"
                )
            self._results_text.insert("end", "\n")

        # 4. Metadata
        model = getattr(result, "model", None)
        latency = getattr(result, "latency_ms", 0.0)
        if model or latency:
            meta_str = f"Model: {model or 'N/A'} | Latency: {latency:.1f}ms\n"
            self._results_text.insert("end", meta_str, "meta")

        self._results_text.configure(state="disabled")
        self._results_text.see("1.0")


class LibraryView(GUIView):
    """
    Document library and knowledge retrieval workspace.

    Provides end-to-end document repository management, file/text ingestion,
    indexing telemetry, document inspection/preview, and semantic/RAG search.
    """

    def __init__(
        self,
        parent: tk.Widget,
        application: Any | None = None,
    ) -> None:
        super().__init__(
            parent,
            title="Knowledge Library",
            description="Search index, browse documents, and inspect retrieved context chunks.",
            name="library",
            application=application,
        )

        # 1. Top Control Bar: Search & Ingestion Operations
        ctrl_frame = ttk.Frame(self.frame)
        ctrl_frame.pack(fill="x", pady=(0, 6))

        # Search Query Bar
        search_box = ttk.Frame(ctrl_frame)
        search_box.pack(fill="x", pady=(0, 4))

        ttk.Label(search_box, text="Search Query:").pack(side="left", padx=(0, 8))
        self._search_entry = ttk.Entry(search_box)
        self._search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._search_entry.bind("<Return>", lambda e: self.search())

        self._search_btn = ttk.Button(
            search_box,
            text="Search",
            command=self.search,
        )
        self._search_btn.pack(side="left", padx=(0, 4))

        # Action Buttons Toolbar
        action_bar = ttk.Frame(ctrl_frame)
        action_bar.pack(fill="x")

        self._import_btn = ttk.Button(
            action_bar,
            text="Import File...",
            command=lambda: self.import_file(async_op=True),
        )
        self._import_btn.pack(side="left", padx=(0, 4))

        self._remove_btn = ttk.Button(
            action_bar,
            text="Remove Document",
            command=lambda: self.remove_selected_document(async_op=True),
        )
        self._remove_btn.pack(side="left", padx=(0, 4))

        self._reindex_btn = ttk.Button(
            action_bar,
            text="Reindex All",
            command=lambda: self.reindex_all(async_op=True),
        )
        self._reindex_btn.pack(side="left", padx=(0, 4))

        self._refresh_btn = ttk.Button(
            action_bar,
            text="Refresh List",
            command=self.refresh_documents,
        )
        self._refresh_btn.pack(side="left", padx=(0, 4))

        # Telemetry / Status Header
        status_bar = ttk.Frame(ctrl_frame)
        status_bar.pack(fill="x", pady=(4, 0))

        self._status_label = ttk.Label(
            status_bar,
            text="Status: Ready",
            font=("TkDefaultFont", 9),
            foreground="#6c757d",
        )
        self._status_label.pack(side="left")

        # 2. Main Content Split Pane
        paned = ttk.PanedWindow(self.frame, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # Left: Document Repository Tree & Preview
        left_pane = ttk.Frame(paned, padding=(0, 4, 4, 0))
        paned.add(left_pane, weight=1)

        doc_box = ttk.LabelFrame(left_pane, text="Indexed Documents", padding=6)
        doc_box.pack(fill="both", expand=True, pady=(0, 6))

        tree_scroll = ttk.Scrollbar(doc_box, orient="vertical")
        self._doc_tree = ttk.Treeview(
            doc_box,
            columns=("id", "title", "chunks", "status"),
            show="headings",
            selectmode="browse",
            height=6,
            yscrollcommand=tree_scroll.set,
        )
        tree_scroll.config(command=self._doc_tree.yview)
        tree_scroll.pack(side="right", fill="y")
        self._doc_tree.pack(side="left", fill="both", expand=True)

        self._doc_tree.heading("id", text="ID")
        self._doc_tree.heading("title", text="Title")
        self._doc_tree.heading("chunks", text="Chunks")
        self._doc_tree.heading("status", text="Status")
        self._doc_tree.column("id", width=70, minwidth=50)
        self._doc_tree.column("title", width=110, minwidth=70)
        self._doc_tree.column("chunks", width=45, minwidth=35)
        self._doc_tree.column("status", width=65, minwidth=45)
        self._doc_tree.bind("<<TreeviewSelect>>", self._on_doc_selected)

        # Preview Frame
        preview_box = ttk.LabelFrame(left_pane, text="Document Preview", padding=6)
        preview_box.pack(fill="both", expand=True)

        self._preview_text = tk.Text(preview_box, wrap="word", height=8)
        self._preview_text.pack(fill="both", expand=True)
        self._preview_text.tag_configure(
            "preview_title", font=("TkDefaultFont", 9, "bold"), foreground="#0d6efd"
        )
        self._preview_text.tag_configure(
            "preview_meta", font=("TkDefaultFont", 8, "italic"), foreground="#6c757d"
        )
        self._preview_text.tag_configure(
            "preview_header", font=("TkDefaultFont", 8, "bold"), foreground="#495057"
        )
        self._preview_text.tag_configure("preview_content", font=("TkDefaultFont", 9))
        self._preview_text.tag_configure(
            "preview_chunk", font=("TkDefaultFont", 8), foreground="#212529"
        )
        self._preview_text.insert(
            "1.0", "Select a document from the list above to inspect its metadata and chunks.\n"
        )
        self._preview_text.configure(state="disabled")

        # Right: Retrieved Chunks & Documents (Search Results)
        right_pane = ttk.Frame(paned, padding=(4, 4, 0, 0))
        paned.add(right_pane, weight=2)

        results_box = ttk.LabelFrame(right_pane, text="Retrieved Chunks & Documents", padding=6)
        results_box.pack(fill="both", expand=True)

        self._display = tk.Text(results_box, wrap="word", height=14)
        self._display.pack(fill="both", expand=True)

        self._display.tag_configure(
            "header", font=("TkDefaultFont", 10, "bold"), foreground="#0d6efd"
        )
        self._display.tag_configure("score", font=("TkDefaultFont", 9), foreground="#6c757d")
        self._display.tag_configure(
            "source", font=("TkDefaultFont", 9, "bold"), foreground="#198754"
        )
        self._display.tag_configure("content", font=("TkDefaultFont", 10))
        self._display.tag_configure(
            "meta", font=("TkDefaultFont", 8, "italic"), foreground="#495057"
        )
        self._display.tag_configure(
            "error", font=("TkDefaultFont", 9, "bold"), foreground="#dc3545"
        )

        self._display.insert(
            "1.0", "Knowledge documents and RAG search results will be shown here.\n"
        )
        self._display.configure(state="disabled")

        self._built = True

        if self._application is not None:
            self.refresh_documents()

    @property
    def doc_tree(self) -> ttk.Treeview:
        return self._doc_tree

    @property
    def preview_text(self) -> tk.Text:
        return self._preview_text

    @property
    def display(self) -> tk.Text:
        return self._display

    @property
    def search_entry(self) -> ttk.Entry:
        return self._search_entry

    @property
    def search_button(self) -> ttk.Button:
        return self._search_btn

    @property
    def import_button(self) -> ttk.Button:
        return self._import_btn

    @property
    def remove_button(self) -> ttk.Button:
        return self._remove_btn

    @property
    def reindex_button(self) -> ttk.Button:
        return self._reindex_btn

    @property
    def refresh_button(self) -> ttk.Button:
        return self._refresh_btn

    @property
    def status_label(self) -> ttk.Label:
        return self._status_label

    def set_application(self, application: Any) -> None:
        super().set_application(application)
        if getattr(self, "_built", False):
            self.refresh_documents()

    def refresh_documents(self, update_status: bool = True) -> None:
        """Populate the document list treeview from the application."""
        if not hasattr(self, "_doc_tree"):
            return
        for item in self._doc_tree.get_children():
            self._doc_tree.delete(item)

        if self.application is not None and hasattr(self.application, "list_documents"):
            try:
                docs = self.application.list_documents()
                for doc in docs:
                    self._doc_tree.insert(
                        "",
                        "end",
                        iid=doc["id"],
                        values=(
                            doc["id"],
                            doc.get("title", doc["id"]),
                            doc.get("chunks_count", 0),
                            doc.get("status", "indexed"),
                        ),
                    )
                if update_status:
                    self._status_label.configure(text=f"Status: {len(docs)} documents indexed")
            except Exception as exc:
                if update_status:
                    self._status_label.configure(text=f"Error listing documents: {exc}")
        else:
            if update_status:
                self._status_label.configure(text="Status: Ready (Offline)")

    def _on_doc_selected(self, event: Any = None) -> None:
        """Handle document selection in the treeview to update preview."""
        selected = self._doc_tree.selection()
        if not selected:
            return
        doc_id = selected[0]
        if self.application is not None and hasattr(self.application, "get_document"):
            try:
                doc_data = self.application.get_document(doc_id)
                if doc_data:
                    self._render_document_preview(doc_data)
            except Exception as exc:
                self._preview_text.configure(state="normal")
                self._preview_text.delete("1.0", "end")
                self._preview_text.insert("end", f"Error loading preview: {exc}\n")
                self._preview_text.configure(state="disabled")

    def _render_document_preview(self, doc_data: dict[str, Any]) -> None:
        """Render selected document details and chunks into preview area."""
        self._preview_text.configure(state="normal")
        self._preview_text.delete("1.0", "end")

        doc_id = doc_data.get("id", "Unknown")
        title = doc_data.get("title", doc_id)
        collection = doc_data.get("collection", "default")
        status = doc_data.get("status", "unknown")
        chunks_count = doc_data.get("chunks_count", 0)
        content_hash = doc_data.get("content_hash", "")
        content = doc_data.get("content", "")
        chunks = doc_data.get("chunks", [])

        self._preview_text.insert("end", f"Document: {title} ({doc_id})\n", "preview_title")
        self._preview_text.insert(
            "end",
            f"Collection: {collection} | Status: {status} | Chunks: {chunks_count}\n",
            "preview_meta",
        )
        if content_hash:
            self._preview_text.insert("end", f"SHA-256: {content_hash[:16]}...\n\n", "preview_meta")
        else:
            self._preview_text.insert("end", "\n")

        self._preview_text.insert("end", "Content Preview:\n", "preview_header")
        display_content = content[:300] + ("..." if len(content) > 300 else "")
        self._preview_text.insert("end", f"{display_content}\n\n", "preview_content")

        if chunks:
            self._preview_text.insert("end", f"Chunks ({len(chunks)}):\n", "preview_header")
            for idx, c in enumerate(chunks, 1):
                c_text = c.get("content", str(c)) if isinstance(c, dict) else str(c)
                snippet = c_text[:100].replace("\n", " ")
                self._preview_text.insert(
                    "end", f"  • Chunk #{idx}: {snippet}...\n", "preview_chunk"
                )

        self._preview_text.configure(state="disabled")
        self._preview_text.see("1.0")

    def search(self, query: str | None = None) -> list[dict[str, Any]]:
        """Synchronously execute knowledge search query (backward-compatible)."""
        q = query.strip() if query is not None else self._search_entry.get().strip()
        if not q:
            return []

        self._display.configure(state="normal")
        self._display.delete("1.0", "end")
        self._display.insert("end", f"Searching for: {q}...\n\n")

        if self.application is not None:
            try:
                results = self.application.search_knowledge(q)
                if not results:
                    self._display.insert("end", "No relevant documents found.\n")
                else:
                    for i, r in enumerate(results, 1):
                        self._display.insert(
                            "end",
                            f"[{i}] Score: {r.get('score', 1.0):.2f} | Source: {r.get('source', 'doc')}\n",
                        )
                        self._display.insert("end", f"    {r.get('content', '')}\n\n")
                self._display.configure(state="disabled")
                self._status_label.configure(text=f"Status: {len(results)} matches found")
                return results
            except Exception as exc:
                self._display.insert("end", f"Knowledge search error: {exc}\n")
                self._display.configure(state="disabled")
                self._status_label.configure(text=f"Search error: {exc}")
                return []
        else:
            self._display.insert("end", f"Simulated search results for: {q}\n")
            self._display.configure(state="disabled")
            self._status_label.configure(text="Status: Completed (Offline)")
            return [
                {
                    "content": f"Sample document context for {q}",
                    "score": 0.95,
                    "source": "simulated",
                }
            ]

    def search_async(
        self,
        query: str | None = None,
        minimum_score: float = 0.0,
        on_complete: Callable[[list[dict[str, Any]]], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Asynchronously execute knowledge search without blocking UI."""
        q = query.strip() if query is not None else self._search_entry.get().strip()
        if not q:
            return

        self._status_label.configure(text=f"Status: Searching for '{q}'...")
        self._search_btn.configure(state="disabled")
        self._display.configure(state="normal")
        self._display.delete("1.0", "end")
        self._display.insert("end", f"Searching for: {q}...\n\n")
        self._display.configure(state="disabled")

        def _on_success(results: list[dict[str, Any]]) -> None:
            self._search_btn.configure(state="normal")
            self._display.configure(state="normal")
            self._display.delete("1.0", "end")
            self._display.insert("end", f"Searching for: {q}...\n\n")
            if not results:
                self._display.insert("end", "No relevant documents found.\n")
            else:
                for i, r in enumerate(results, 1):
                    self._display.insert(
                        "end",
                        f"[{i}] Score: {r.get('score', 1.0):.2f} | Source: {r.get('source', 'doc')}\n",
                    )
                    self._display.insert("end", f"    {r.get('content', '')}\n\n")
            self._display.configure(state="disabled")
            self._status_label.configure(text=f"Status: {len(results)} matches found")
            if on_complete:
                on_complete(results)

        def _on_err(exc: Exception) -> None:
            self._search_btn.configure(state="normal")
            self._display.configure(state="normal")
            self._display.insert("end", f"Knowledge search error: {exc}\n")
            self._display.configure(state="disabled")
            self._status_label.configure(text=f"Search error: {exc}")
            if on_error:
                on_error(exc)

        if self.application is not None and hasattr(self.application, "search_knowledge_async"):
            self.application.search_knowledge_async(
                q,
                on_complete=_on_success,
                on_error=_on_err,
                minimum_score=minimum_score,
            )
        else:
            try:
                res = self.search(q)
                _on_success(res)
            except Exception as e:
                _on_err(e)

    def import_file(
        self,
        file_path: str | Path | None = None,
        async_op: bool = False,
        on_complete: Callable[[dict[str, Any]], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Import a file into the knowledge repository."""
        path_to_import = file_path
        if path_to_import is None:
            try:
                from tkinter import filedialog

                chosen = filedialog.askopenfilename(
                    title="Import Document into ScholarOS",
                    filetypes=[
                        ("Supported Files", "*.txt;*.md;*.json;*.pdf"),
                        ("All Files", "*.*"),
                    ],
                )
                if chosen:
                    path_to_import = chosen
            except Exception:
                path_to_import = None

        if not path_to_import:
            return

        p = Path(path_to_import)
        self._status_label.configure(text=f"Status: Importing {p.name}...")

        def _on_imported(doc_info: dict[str, Any]) -> None:
            self.refresh_documents(update_status=False)
            title = doc_info.get("title", p.name)
            chunks = doc_info.get("chunks_count", 0)
            self._status_label.configure(text=f"Status: Imported '{title}' ({chunks} chunks)")
            if on_complete:
                on_complete(doc_info)

        def _on_err(exc: Exception) -> None:
            self._status_label.configure(text=f"Import error: {exc}")
            if on_error:
                on_error(exc)

        if (
            async_op
            and self.application is not None
            and hasattr(self.application, "add_document_async")
        ):
            self.application.add_document_async(
                document_or_path=p,
                on_complete=_on_imported,
                on_error=_on_err,
            )
        elif self.application is not None and hasattr(self.application, "add_document"):
            try:
                doc_info = self.application.add_document(document_or_path=p)
                _on_imported(doc_info)
            except Exception as exc:
                _on_err(exc)

    def add_text_document(
        self,
        title: str,
        content: str,
        collection: str = "default",
        async_op: bool = False,
        on_complete: Callable[[dict[str, Any]], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Add a raw text document directly into the knowledge repository."""
        self._status_label.configure(text=f"Status: Adding '{title}'...")

        def _on_added(doc_info: dict[str, Any]) -> None:
            self.refresh_documents(update_status=False)
            chunks = doc_info.get("chunks_count", 0)
            self._status_label.configure(text=f"Status: Added '{title}' ({chunks} chunks)")
            if on_complete:
                on_complete(doc_info)

        def _on_err(exc: Exception) -> None:
            self._status_label.configure(text=f"Add error: {exc}")
            if on_error:
                on_error(exc)

        if (
            async_op
            and self.application is not None
            and hasattr(self.application, "add_document_async")
        ):
            self.application.add_document_async(
                document_or_path=content,
                title=title,
                content=content,
                collection_name=collection,
                on_complete=_on_added,
                on_error=_on_err,
            )
        elif self.application is not None and hasattr(self.application, "add_document"):
            try:
                doc_info = self.application.add_document(
                    document_or_path=content,
                    title=title,
                    content=content,
                    collection_name=collection,
                )
                _on_added(doc_info)
            except Exception as exc:
                _on_err(exc)

    def remove_selected_document(
        self,
        async_op: bool = False,
        on_complete: Callable[[bool], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Remove the currently selected document from the knowledge base."""
        selected = self._doc_tree.selection()
        if not selected:
            return
        doc_id = selected[0]
        self._status_label.configure(text=f"Status: Removing document '{doc_id}'...")

        def _on_removed(success: bool) -> None:
            if success:
                self.refresh_documents(update_status=False)
                self._status_label.configure(text=f"Status: Removed document '{doc_id}'")
                self._preview_text.configure(state="normal")
                self._preview_text.delete("1.0", "end")
                self._preview_text.insert(
                    "1.0",
                    "Select a document from the list above to inspect its metadata and chunks.\n",
                )
                self._preview_text.configure(state="disabled")
            else:
                self._status_label.configure(text=f"Failed to remove document '{doc_id}'")
            if on_complete:
                on_complete(success)

        def _on_err(exc: Exception) -> None:
            self._status_label.configure(text=f"Remove error: {exc}")
            if on_error:
                on_error(exc)

        if (
            async_op
            and self.application is not None
            and hasattr(self.application, "remove_document_async")
        ):
            self.application.remove_document_async(
                doc_id,
                on_complete=_on_removed,
                on_error=_on_err,
            )
        elif self.application is not None and hasattr(self.application, "remove_document"):
            try:
                success = self.application.remove_document(doc_id)
                _on_removed(success)
            except Exception as exc:
                _on_err(exc)

    def reindex_all(
        self,
        async_op: bool = False,
        on_complete: Callable[[int], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Re-index all documents in the knowledge repository."""
        self._status_label.configure(text="Status: Reindexing collections...")

        def _on_done(chunks: int) -> None:
            self.refresh_documents(update_status=False)
            self._status_label.configure(
                text=f"Status: Reindexing complete ({chunks} chunks indexed)"
            )
            if on_complete:
                on_complete(chunks)

        def _on_err(exc: Exception) -> None:
            self._status_label.configure(text=f"Reindexing error: {exc}")
            if on_error:
                on_error(exc)

        if (
            async_op
            and self.application is not None
            and hasattr(self.application, "reindex_knowledge_async")
        ):
            self.application.reindex_knowledge_async(
                on_complete=_on_done,
                on_error=_on_err,
            )
        elif self.application is not None and hasattr(self.application, "reindex_knowledge"):
            try:
                chunks = self.application.reindex_knowledge()
                _on_done(chunks)
            except Exception as exc:
                _on_err(exc)


class PluginsView(GUIView):
    """
    Plugin inspection and management workspace.
    """

    def __init__(
        self,
        parent: tk.Widget,
        application: Any | None = None,
    ) -> None:
        super().__init__(
            parent,
            title="Plugins & Extensibility",
            description="Inspect active plugins, verify sandboxing, and toggle features.",
            name="plugins",
            application=application,
        )

        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill="x", pady=(0, 10))

        ttk.Button(
            toolbar,
            text="Refresh Plugins",
            command=self.refresh,
        ).pack(side="left")

        # Plugin list
        container = ttk.LabelFrame(self.frame, text="Registered Plugins", padding=10)
        container.pack(fill="both", expand=True)

        self._list_text = tk.Text(container, wrap="word", height=10)
        self._list_text.pack(fill="both", expand=True)
        self._built = True
        self.refresh()

    def refresh(self) -> list[dict[str, Any]]:
        self._list_text.configure(state="normal")
        self._list_text.delete("1.0", "end")

        if self.application is not None:
            raw_plugins = self.application.list_plugins()
            plugins: list[dict[str, Any]] = (
                list(raw_plugins) if isinstance(raw_plugins, (list, tuple)) else []
            )
            if not plugins:
                self._list_text.insert("end", "No plugins registered.\n")
            else:
                for p in plugins:
                    self._list_text.insert(
                        "end",
                        f"• {p.get('name', 'plugin')} (v{p.get('version', '1.0')}): "
                        f"Status={p.get('state', 'UNKNOWN')} - {p.get('description', '')}\n",
                    )
            self._list_text.configure(state="disabled")
            return plugins

        self._list_text.insert("end", "Plugin manager not connected.\n")
        self._list_text.configure(state="disabled")
        return []


class SettingsView(GUIView):
    """
    Settings, model selection, and provider configuration workspace.
    """

    def __init__(
        self,
        parent: tk.Widget,
        application: Any | None = None,
    ) -> None:
        super().__init__(
            parent,
            title="Settings & System Configuration",
            description="Select AI providers, configure default models, and view system health.",
            name="settings",
            application=application,
        )

        # Provider & Model Configuration Frame
        prov_frame = ttk.LabelFrame(self.frame, text="AI & Provider Configuration", padding=10)
        prov_frame.pack(fill="x", pady=(0, 10))

        # Provider row
        row1 = ttk.Frame(prov_frame)
        row1.pack(fill="x", pady=(0, 6))
        ttk.Label(row1, text="Provider:", width=12).pack(side="left")
        self._provider_combo = ttk.Combobox(
            row1,
            values=["ollama", "openai", "anthropic", "mock"],
            state="readonly",
            width=18,
        )
        self._provider_combo.set("ollama")
        self._provider_combo.pack(side="left", padx=(0, 8))

        ttk.Button(
            row1,
            text="Switch Provider",
            command=self.apply_provider,
        ).pack(side="left", padx=(0, 12))

        ttk.Label(row1, text="Base URL:").pack(side="left", padx=(0, 6))
        self._base_url_entry = ttk.Entry(row1, width=28)
        self._base_url_entry.insert(0, "http://localhost:11434")
        self._base_url_entry.pack(side="left", fill="x", expand=True)

        # API Key row with secret masking toggle
        row2 = ttk.Frame(prov_frame)
        row2.pack(fill="x", pady=(0, 6))
        ttk.Label(row2, text="API Key:", width=12).pack(side="left")
        self._api_key_entry = ttk.Entry(row2, show="*", width=32)
        self._api_key_entry.pack(side="left", padx=(0, 8))

        self._show_key_var = tk.BooleanVar(value=False)
        self._show_key_cb = ttk.Checkbutton(
            row2,
            text="Show Secret",
            variable=self._show_key_var,
            command=self.toggle_key_visibility,
        )
        self._show_key_cb.pack(side="left")

        # Models row
        row3 = ttk.Frame(prov_frame)
        row3.pack(fill="x")
        ttk.Label(row3, text="Chat Model:", width=12).pack(side="left")
        self._chat_model_entry = ttk.Entry(row3, width=22)
        self._chat_model_entry.insert(0, "qwen2.5:1.5b")
        self._chat_model_entry.pack(side="left", padx=(0, 12))

        ttk.Label(row3, text="Research Model:").pack(side="left", padx=(0, 6))
        self._research_model_entry = ttk.Entry(row3, width=22)
        self._research_model_entry.insert(0, "qwen2.5:1.5b")
        self._research_model_entry.pack(side="left")

        # RAG & Retrieval Frame
        rag_frame = ttk.LabelFrame(self.frame, text="RAG & Retrieval Configuration", padding=10)
        rag_frame.pack(fill="x", pady=(0, 10))

        rag_row = ttk.Frame(rag_frame)
        rag_row.pack(fill="x")
        ttk.Label(rag_row, text="Strategy:", width=12).pack(side="left")
        self._rag_strategy_combo = ttk.Combobox(
            rag_row,
            values=["default", "hybrid", "semantic", "keyword"],
            state="readonly",
            width=14,
        )
        self._rag_strategy_combo.set("hybrid")
        self._rag_strategy_combo.pack(side="left", padx=(0, 12))

        ttk.Label(rag_row, text="Result Limit:").pack(side="left", padx=(0, 6))
        self._rag_limit_entry = ttk.Entry(rag_row, width=8)
        self._rag_limit_entry.insert(0, "10")
        self._rag_limit_entry.pack(side="left", padx=(0, 12))

        ttk.Label(rag_row, text="Workspace Dir:").pack(side="left", padx=(0, 6))
        self._workspace_entry = ttk.Entry(rag_row, width=20)
        self._workspace_entry.insert(0, "workspace")
        self._workspace_entry.pack(side="left", fill="x", expand=True)

        # Action Buttons row
        action_row = ttk.Frame(self.frame)
        action_row.pack(fill="x", pady=(0, 10))

        ttk.Button(
            action_row,
            text="Save Settings",
            command=self.save_settings,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            action_row,
            text="Reload Configuration",
            command=self.refresh,
        ).pack(side="left")

        # Telemetry info
        info_frame = ttk.LabelFrame(self.frame, text="System Environment & Diagnostics", padding=10)
        info_frame.pack(fill="both", expand=True)

        self._info_display = tk.Text(info_frame, wrap="word", height=6)
        self._info_display.pack(fill="both", expand=True)
        self._built = True
        self.refresh()

    def toggle_key_visibility(self) -> None:
        """Toggle show/hide for the API key password field."""
        if self._show_key_var.get():
            self._api_key_entry.configure(show="")
        else:
            self._api_key_entry.configure(show="*")

    def load_from_config(self) -> None:
        """Populate form controls from active application configuration."""
        if self.application is None:
            return
        if not hasattr(self.application, "get_config"):
            return

        try:
            cfg = self.application.get_config()
            if hasattr(cfg, "ai"):
                if cfg.ai.provider:
                    self._provider_combo.set(cfg.ai.provider)
                if cfg.ai.base_url:
                    self._base_url_entry.delete(0, "end")
                    self._base_url_entry.insert(0, cfg.ai.base_url)
                if cfg.ai.api_key:
                    self._api_key_entry.delete(0, "end")
                    self._api_key_entry.insert(0, cfg.ai.api_key)
            if hasattr(cfg, "models"):
                if cfg.models.default_chat_model:
                    self._chat_model_entry.delete(0, "end")
                    self._chat_model_entry.insert(0, cfg.models.default_chat_model)
                if cfg.models.default_research_model:
                    self._research_model_entry.delete(0, "end")
                    self._research_model_entry.insert(0, cfg.models.default_research_model)
            if hasattr(cfg, "rag"):
                if cfg.rag.default_strategy:
                    self._rag_strategy_combo.set(cfg.rag.default_strategy)
                self._rag_limit_entry.delete(0, "end")
                self._rag_limit_entry.insert(0, str(cfg.rag.default_limit))
            if hasattr(cfg, "storage") and cfg.storage.workspace:
                self._workspace_entry.delete(0, "end")
                self._workspace_entry.insert(0, str(cfg.storage.workspace))
        except Exception:
            pass

    def save_settings(self) -> dict[str, Any] | None:
        """Collect form values, update configuration, and persist to disk."""
        updates: dict[str, Any] = {
            "ai": {
                "provider": self._provider_combo.get(),
                "base_url": self._base_url_entry.get().strip(),
            },
            "models": {
                "default_chat_model": self._chat_model_entry.get().strip(),
                "default_research_model": self._research_model_entry.get().strip(),
            },
            "rag": {
                "default_strategy": self._rag_strategy_combo.get(),
                "default_limit": int(self._rag_limit_entry.get().strip() or "10"),
            },
            "storage": {
                "workspace": self._workspace_entry.get().strip(),
            },
        }

        api_key = self._api_key_entry.get().strip()
        if api_key:
            updates["ai"]["api_key"] = api_key

        if self.application is not None and hasattr(self.application, "update_config"):
            try:
                self.application.update_config(updates, persist=True)
                if hasattr(self.application, "set_status"):
                    self.application.set_status("Settings updated and persisted successfully.")
                self.refresh()
                return updates
            except Exception as exc:
                if hasattr(self.application, "set_status"):
                    self.application.set_status(f"Failed to update settings: {exc}", error=True)
                return None
        return updates

    def apply_provider(self) -> None:
        chosen = self._provider_combo.get()
        if self.application is not None:
            try:
                self.application.set_provider(chosen)
                if hasattr(self.application, "set_status"):
                    self.application.set_status(f"Active provider switched to '{chosen}'")
            except Exception as exc:
                if hasattr(self.application, "set_status"):
                    self.application.set_status(f"Error switching provider: {exc}", error=True)
        self.refresh()

    def refresh(self) -> None:
        self.load_from_config()
        self._info_display.configure(state="normal")
        self._info_display.delete("1.0", "end")

        if self.application is not None:
            raw_info = self.application.info()
            info = raw_info if isinstance(raw_info, dict) else {}

            runtime_status = info.get("status", "READY")
            runtime_connected = (
                "Connected"
                if runtime_status in ("READY", "RUNNING", "INITIALIZED")
                else runtime_status
            )

            active_provider = info.get("active_provider")
            if (
                not active_provider
                and hasattr(self.application, "ai_manager")
                and self.application.ai_manager is not None
            ):
                active_provider = getattr(self.application.ai_manager, "default_provider", None)
            provider_display = str(active_provider).capitalize() if active_provider else "None"

            active_model = info.get("active_model")
            if (
                not active_model
                and hasattr(self.application, "config")
                and self.application.config is not None
            ):
                if hasattr(self.application.config, "models") and hasattr(
                    self.application.config.models, "default_chat_model"
                ):
                    active_model = self.application.config.models.default_chat_model
            if not active_model and hasattr(self, "_chat_model_entry"):
                val = self._chat_model_entry.get().strip()
                if val:
                    active_model = val
            model_display = active_model or "None"

            pm_status = "Connected" if info.get("plugins") else "Not Connected"
            km_status = "Ready" if (info.get("knowledge") or info.get("rag")) else "Offline"

            self._info_display.insert("end", f"Runtime: {runtime_connected}\n")
            self._info_display.insert("end", f"Provider: {provider_display}\n")
            self._info_display.insert("end", f"Model: {model_display}\n")
            self._info_display.insert("end", f"Plugin Manager: {pm_status}\n")
            self._info_display.insert("end", f"Knowledge: {km_status}\n")
        else:
            self._info_display.insert("end", "Application layer: Offline / Mock\n")

        self._info_display.configure(state="disabled")
