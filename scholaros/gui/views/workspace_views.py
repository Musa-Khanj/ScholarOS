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

        # Hook send button
        if self._chat.send_button is not None:
            self._chat.send_button.configure(command=self.send_message)

    @property
    def frame(self) -> ttk.Frame:
        return self._chat.frame

    @property
    def chat(self) -> GUIChat:
        return self._chat

    @property
    def application(self) -> Any | None:
        return self._application

    def set_application(self, application: Any) -> None:
        self._application = application

    def show(self) -> None:
        if hasattr(self.frame, "tkraise"):
            self.frame.tkraise()

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
                self._chat.append_message("ScholarOS", response)
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

    def clear(self) -> None:
        self._chat.clear()


class ResearchView(GUIView):
    """
    Research workspace for running queries, synthesis, and viewing findings.
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

        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(input_frame, text="Topic / Query:").pack(side="left", padx=(0, 8))
        self._entry = ttk.Entry(input_frame)
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._run_btn = ttk.Button(
            input_frame,
            text="Run Research",
            command=self.run_research,
        )
        self._run_btn.pack(side="left")

        # Results area
        results_frame = ttk.LabelFrame(self.frame, text="Research Results & Citations", padding=10)
        results_frame.pack(fill="both", expand=True)

        self._results_text = tk.Text(results_frame, wrap="word", height=12)
        self._results_text.pack(fill="both", expand=True)
        self._results_text.insert("1.0", "Enter a topic above and click 'Run Research'.\n")
        self._results_text.configure(state="disabled")

        self._built = True

    def run_research(self, topic: str | None = None) -> Any:
        query = topic or self._entry.get().strip()
        if not query:
            return None

        self._results_text.configure(state="normal")
        self._results_text.delete("1.0", "end")
        self._results_text.insert("end", f"Executing research on: {query}...\n\n")

        if self.application is not None:
            try:
                result = self.application.research(query)
                answer = getattr(result, "content", getattr(result, "answer", str(result)))
                self._results_text.insert("end", f"Findings:\n{answer}\n")
                self._results_text.configure(state="disabled")
                return result
            except Exception as exc:
                self._results_text.insert("end", f"Error during research: {exc}\n")
                self._results_text.configure(state="disabled")
                if hasattr(self.application, "set_status"):
                    self.application.set_status(str(exc), error=True)
                return None
        else:
            self._results_text.insert("end", f"Research pipeline simulated for: {query}\n")
            self._results_text.configure(state="disabled")
            return f"Research results for {query}"


class LibraryView(GUIView):
    """
    Document library and knowledge retrieval workspace.
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

        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Search Query:").pack(side="left", padx=(0, 8))
        self._search_entry = ttk.Entry(search_frame)
        self._search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._search_btn = ttk.Button(
            search_frame,
            text="Search",
            command=self.search,
        )
        self._search_btn.pack(side="left")

        # Results viewer
        results_box = ttk.LabelFrame(self.frame, text="Retrieved Chunks & Documents", padding=10)
        results_box.pack(fill="both", expand=True)

        self._display = tk.Text(results_box, wrap="word", height=12)
        self._display.pack(fill="both", expand=True)
        self._display.insert("1.0", "Knowledge documents and RAG search results will be shown here.\n")
        self._display.configure(state="disabled")

        self._built = True

    def search(self, query: str | None = None) -> list[dict[str, Any]]:
        q = query or self._search_entry.get().strip()
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
                        self._display.insert("end", f"[{i}] Score: {r.get('score', 1.0):.2f} | Source: {r.get('source', 'doc')}\n")
                        self._display.insert("end", f"    {r.get('content', '')}\n\n")
                self._display.configure(state="disabled")
                return results
            except Exception as exc:
                self._display.insert("end", f"Knowledge search error: {exc}\n")
                self._display.configure(state="disabled")
                return []
        else:
            self._display.insert("end", f"Simulated search results for: {q}\n")
            self._display.configure(state="disabled")
            return [{"content": f"Sample document context for {q}", "score": 0.95, "source": "simulated"}]


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
            plugins = self.application.list_plugins()
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
            info = self.application.info()
            for k, v in info.items():
                self._info_display.insert("end", f"{k.replace('_', ' ').title()}: {v}\n")
        else:
            self._info_display.insert("end", "Application layer: Offline / Mock\n")

        self._info_display.configure(state="disabled")
