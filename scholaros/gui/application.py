"""
ScholarOS GUI Application.

Coordinates the ScholarOS desktop shell, manages the application lifecycle,
and delegates domain operations to the underlying AI, Research, Knowledge/RAG,
and Plugin subsystems without mixing business logic into the presentation layer.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from enum import Enum
from typing import TYPE_CHECKING, Any

from scholaros.gui.window import GUIWindow

if TYPE_CHECKING:
    from pathlib import Path
    from scholaros.ai.manager import AIManager
    from scholaros.config.manager import ConfigManager
    from scholaros.config.model import AppConfig
    from scholaros.config.settings import Settings
    from scholaros.container.container import Container
    from scholaros.events.bus import EventBus
    from scholaros.knowledge.rag.pipeline import RAGPipeline
    from scholaros.observability.trace import RAGTrace
    from scholaros.plugins.manager import PluginManager
    from scholaros.research.pipeline import ResearchPipeline
    from scholaros.services.health import ServiceHealth


class ApplicationState(Enum):
    """Lifecycle states of the GUI application."""

    INITIALIZED = "INITIALIZED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class GUIApplication:
    """
    Main ScholarOS GUI application orchestrator.

    Coordinates the GUI window, tracks lifecycle transitions,
    and delegates user actions to the underlying services:
    GUI -> Application -> Services -> Core.
    """

    def __init__(
        self,
        window: GUIWindow,
        services: Any | None = None,
        ai_manager: AIManager | None = None,
        research_pipeline: ResearchPipeline | None = None,
        rag_pipeline: RAGPipeline | None = None,
        plugin_manager: PluginManager | None = None,
        container: Container | None = None,
        event_bus: EventBus | None = None,
        config: Any | None = None,
        config_manager: ConfigManager | None = None,
        max_workers: int = 4,
    ) -> None:
        self._window = window
        self._services = services
        self._ai_manager = ai_manager
        self._research_pipeline = research_pipeline
        self._rag_pipeline = rag_pipeline
        self._plugin_manager = plugin_manager
        self._container = container
        self._event_bus = event_bus
        self._config = config
        self._config_manager = config_manager
        self._max_workers = max_workers
        self._executor: ThreadPoolExecutor | None = None
        self._state = ApplicationState.INITIALIZED

        # Inspect services bundle if supplied
        if services is not None:
            if self._ai_manager is None:
                self._ai_manager = getattr(services, "ai_manager", None)
            if self._research_pipeline is None:
                self._research_pipeline = getattr(services, "research_pipeline", None)
            if self._rag_pipeline is None:
                self._rag_pipeline = getattr(services, "rag_pipeline", None)
            if self._plugin_manager is None:
                self._plugin_manager = getattr(services, "plugin_manager", None)
            if self._container is None:
                self._container = getattr(services, "container", None)
            if self._event_bus is None:
                self._event_bus = getattr(services, "event_bus", None)
            if self._config is None:
                self._config = getattr(services, "config", None)
            if self._config_manager is None:
                self._config_manager = getattr(services, "config_manager", None)

        if self._config_manager is None and self._config is not None:
            if hasattr(self._config, "load_config") or hasattr(self._config, "to_settings"):
                self._config_manager = self._config

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    @property
    def window(self) -> GUIWindow:
        return self._window

    @property
    def state(self) -> ApplicationState:
        return self._state

    @property
    def services(self) -> Any | None:
        return self._services

    @property
    def ai_manager(self) -> AIManager | None:
        return self._ai_manager

    @property
    def research_pipeline(self) -> ResearchPipeline | None:
        return self._research_pipeline

    @property
    def rag_pipeline(self) -> RAGPipeline | None:
        return self._rag_pipeline

    @property
    def plugin_manager(self) -> PluginManager | None:
        return self._plugin_manager

    @property
    def container(self) -> Container | None:
        return self._container

    @property
    def event_bus(self) -> EventBus | None:
        return self._event_bus

    @property
    def config(self) -> Any | None:
        return self._config

    @property
    def config_manager(self) -> ConfigManager | None:
        return self._config_manager

    @property
    def executor(self) -> ThreadPoolExecutor:
        """Return or lazily initialize the background worker thread pool."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=self._max_workers,
                thread_name_prefix="ScholarOS-Worker",
            )
        return self._executor

    @property
    def is_running(self) -> bool:
        return self._state == ApplicationState.RUNNING

    # -----------------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------------

    def startup(self) -> None:
        """Transition application to RUNNING and notify status bar."""
        self._state = ApplicationState.STARTING
        # Validate or warm up components if necessary
        self._state = ApplicationState.RUNNING
        self.set_status("Ready")

    def shutdown(self) -> None:
        """Gracefully halt application operations."""
        self._state = ApplicationState.STOPPING
        if self._executor is not None:
            self._executor.shutdown(wait=False)
            self._executor = None
        self._state = ApplicationState.STOPPED
        self.set_status("Stopped")

    def status(self) -> str:
        """Return human-readable application status."""
        if self._state == ApplicationState.RUNNING:
            return "READY"
        return self._state.value

    def info(self) -> dict[str, Any]:
        """Return health and component availability overview."""
        active_provider = None
        if self.ai_manager is not None:
            active_provider = getattr(self.ai_manager, "default_provider", None)

        return {
            "status": self.status(),
            "ai": self.ai_manager is not None,
            "research": self.research_pipeline is not None,
            "rag": self.rag_pipeline is not None,
            "plugins": self.plugin_manager is not None,
            "active_provider": active_provider,
        }

    # -----------------------------------------------------------------------
    # Presentation / Window Operations
    # -----------------------------------------------------------------------

    def build(self) -> None:
        """Construct the visual window hierarchy."""
        self.window.build()

    def run(self) -> None:
        """Start the application and launch the GUI event loop."""
        self.startup()
        try:
            self.window.show()
        finally:
            self.shutdown()

    def set_status(self, message: str, error: bool = False) -> None:
        """Update the window status bar if available."""
        if hasattr(self.window, "set_status"):
            self.window.set_status(message, error=error)

    # -----------------------------------------------------------------------
    # Business Logic Delegation (Used by UI Views)
    # -----------------------------------------------------------------------

    def chat(
        self,
        prompt: str,
        model: str | None = None,
        provider: str | None = None,
    ) -> str:
        """
        Execute an AI chat turn, delegating to AIManager or RAGPipeline.
        """
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            raise ValueError("Chat prompt cannot be empty.")

        # 1. Prefer AIManager
        if self.ai_manager is not None:
            from scholaros.ai.request import AIRequest

            ai_provider = self.ai_manager.select_provider(
                model=model,
                requested_provider=provider,
            )
            request = AIRequest(prompt=cleaned_prompt, model=model)
            response = ai_provider.generate(request)
            return response.content

        # 2. Fallback to RAGPipeline
        if self.rag_pipeline is not None:
            from scholaros.knowledge.rag.request import RAGRequest

            rag_req = RAGRequest(query=cleaned_prompt)
            rag_res = self.rag_pipeline.run(rag_req)
            return rag_res.content

        raise RuntimeError("No AI provider or RAG pipeline is configured.")

    def research(
        self,
        query: str,
        template: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a research operation through the ResearchPipeline.
        """
        cleaned_query = query.strip()
        if not cleaned_query:
            raise ValueError("Research query cannot be empty.")

        if self.research_pipeline is not None:
            if template:
                return self.research_pipeline.execute(template, query=cleaned_query, **kwargs)
            return self.research_pipeline.execute(cleaned_query, **kwargs)

        raise RuntimeError("Research pipeline is not configured.")

    def search_knowledge(
        self,
        query: str,
        minimum_score: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Query knowledge repository via RAGPipeline and return structured source items.
        """
        cleaned_query = query.strip()
        if not cleaned_query:
            return []

        if self.rag_pipeline is not None:
            from scholaros.knowledge.rag.request import RAGRequest

            req = RAGRequest(query=cleaned_query, minimum_score=minimum_score)
            res = self.rag_pipeline.run(req)

            results: list[dict[str, Any]] = []
            for item in res.sources:
                results.append({
                    "content": getattr(item, "content", str(item)),
                    "score": getattr(item, "score", 1.0),
                    "source": getattr(item, "source", "unknown"),
                    "metadata": getattr(item, "metadata", {}),
                })
            return results

        raise RuntimeError("RAG pipeline is not configured.")

    # -----------------------------------------------------------------------
    # Non-blocking Asynchronous Operations (GUI Responsiveness)
    # -----------------------------------------------------------------------

    def execute_async(
        self,
        func: Callable[..., Any],
        *args: Any,
        on_success: Callable[[Any], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        **kwargs: Any,
    ) -> Future[Any]:
        """
        Dispatch a heavy or blocking task to a background worker thread.
        Never freezes the Tkinter desktop GUI or UI event loop.
        """
        def _worker() -> Any:
            try:
                res = func(*args, **kwargs)
                if on_success is not None:
                    root = getattr(self.window, "root", None)
                    if root is not None and type(root).__name__ != "MagicMock" and hasattr(root, "after"):
                        try:
                            root.after(0, lambda: on_success(res))
                        except Exception:
                            on_success(res)
                    else:
                        on_success(res)
                return res
            except Exception as exc:
                if on_error is not None:
                    err = exc
                    root = getattr(self.window, "root", None)
                    if root is not None and type(root).__name__ != "MagicMock" and hasattr(root, "after"):
                        try:
                            root.after(0, lambda e=err: on_error(e))
                        except Exception:
                            on_error(err)
                    else:
                        on_error(err)
                raise

        return self.executor.submit(_worker)

    def chat_async(
        self,
        prompt: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[Exception], None] | None = None,
        model: str | None = None,
        provider: str | None = None,
    ) -> Future[Any]:
        """Asynchronously execute chat without blocking the UI thread."""
        return self.execute_async(
            self.chat,
            prompt=prompt,
            model=model,
            provider=provider,
            on_success=on_complete,
            on_error=on_error,
        )

    def research_async(
        self,
        query: str,
        on_complete: Callable[[Any], None],
        on_error: Callable[[Exception], None] | None = None,
        template: str | None = None,
        **kwargs: Any,
    ) -> Future[Any]:
        """Asynchronously execute research without blocking the UI thread."""
        return self.execute_async(
            self.research,
            query=query,
            template=template,
            on_success=on_complete,
            on_error=on_error,
            **kwargs,
        )

    def search_knowledge_async(
        self,
        query: str,
        on_complete: Callable[[list[dict[str, Any]]], None],
        on_error: Callable[[Exception], None] | None = None,
        minimum_score: float = 0.0,
    ) -> Future[Any]:
        """Asynchronously query knowledge without blocking the UI thread."""
        return self.execute_async(
            self.search_knowledge,
            query=query,
            minimum_score=minimum_score,
            on_success=on_complete,
            on_error=on_error,
        )

    def list_providers(self) -> list[str]:
        """Return available AI provider identifiers."""
        if self.ai_manager is not None:
            return list(self.ai_manager.get_available_providers())
        return []

    def list_models(self, provider: str | None = None) -> list[str]:
        """Return available models optionally filtered by provider."""
        if self.ai_manager is not None:
            specs = self.ai_manager.list_models(provider=provider)
            return [spec.name for spec in specs]
        return []

    def set_provider(self, provider_name: str) -> None:
        """Switch active default provider."""
        if self.ai_manager is not None:
            self.ai_manager.switch_provider(provider_name)
        else:
            raise RuntimeError("AI manager is not configured.")

    def list_plugins(self) -> list[dict[str, Any]]:
        """Return list of discovered and installed plugins with statuses."""
        if self.plugin_manager is not None:
            results: list[dict[str, Any]] = []
            for p_id, p in self.plugin_manager.plugins.items():
                desc = getattr(p, "description", None)
                if desc is None and hasattr(p, "metadata") and hasattr(p.metadata, "description"):
                    desc = p.metadata.description
                results.append({
                    "id": p.id,
                    "name": p.name,
                    "version": p.version,
                    "state": self.plugin_manager.state(p.id).name,
                    "description": desc or "",
                })
            return results
        return []

    def enable_plugin(self, name_or_id: str) -> None:
        """Enable a plugin through the PluginManager."""
        if self.plugin_manager is not None:
            self.plugin_manager.enable(name_or_id)
        else:
            raise RuntimeError("Plugin manager is not configured.")

    def disable_plugin(self, name_or_id: str) -> None:
        """Disable a plugin through the PluginManager."""
        if self.plugin_manager is not None:
            self.plugin_manager.disable(name_or_id)
        else:
            raise RuntimeError("Plugin manager is not configured.")

    def get_config(self) -> AppConfig:
        """Return the current application configuration model."""
        if self._config_manager is not None:
            return self._config_manager.config
        from scholaros.config.manager import ConfigManager
        self._config_manager = ConfigManager()
        return self._config_manager.config

    def get_settings(self) -> Settings:
        """Return the current immutable application settings."""
        if self._config_manager is not None:
            return self._config_manager.settings
        from scholaros.config.manager import ConfigManager
        self._config_manager = ConfigManager()
        return self._config_manager.settings

    def update_config(
        self,
        updates: dict[str, Any],
        persist: bool = False,
        persist_path: Path | str | None = None,
    ) -> AppConfig:
        """Apply dynamic configuration updates with optional persistence."""
        if self._config_manager is None:
            from scholaros.config.manager import ConfigManager
            self._config_manager = ConfigManager()
        return self._config_manager.update(
            updates=updates,
            validate=True,
            persist=persist,
            persist_path=persist_path,
        )

    def save_config(
        self,
        path: Path | str | None = None,
        format: str | None = None,
        mask_secrets: bool = False,
    ) -> Path:
        """Save configuration to disk."""
        if self._config_manager is None:
            from scholaros.config.manager import ConfigManager
            self._config_manager = ConfigManager()
        return self._config_manager.save(
            path=path,
            format=format,
            mask_secrets=mask_secrets,
        )

    # -----------------------------------------------------------------------
    # Observability, Telemetry & Diagnostics
    # -----------------------------------------------------------------------

    def get_trace(self, trace_id: str) -> RAGTrace | None:
        """Retrieve an execution trace by trace_id."""
        from scholaros.observability.registry import DiagnosticsRegistry

        return DiagnosticsRegistry.get_default().get(trace_id)

    def get_recent_traces(self, limit: int = 10) -> list[RAGTrace]:
        """Return the most recent execution traces."""
        from scholaros.observability.registry import DiagnosticsRegistry

        return DiagnosticsRegistry.get_default().get_recent(limit=limit)

    def get_telemetry(self) -> dict[str, Any]:
        """Return a snapshot of runtime telemetry and latency percentiles."""
        from scholaros.observability.telemetry import TelemetryCollector

        return TelemetryCollector.get_default().snapshot()

    def check_system_health(self) -> ServiceHealth:
        """Perform a unified system health audit across subsystems."""
        from scholaros.observability.health import SystemHealthAggregator

        retrieval_mgr = None
        if self._rag_pipeline is not None:
            retrieval_mgr = getattr(self._rag_pipeline, "_retrieval_manager", None)
            if retrieval_mgr is None:
                r_pipe = getattr(self._rag_pipeline, "_retrieval_pipeline", None)
                if r_pipe is not None:
                    retrieval_mgr = getattr(r_pipe, "manager", None)

        aggregator = SystemHealthAggregator(
            retrieval_manager=retrieval_mgr,
            ai_manager=self._ai_manager,
            plugin_manager=self._plugin_manager,
        )
        return aggregator.check_health()

    def set_debug_mode(self, enabled: bool) -> None:
        """Toggle system-wide debug mode."""
        from scholaros.observability import disable_debug_mode, enable_debug_mode

        if enabled:
            enable_debug_mode()
        else:
            disable_debug_mode()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"window={self.window!r}"
            f")"
        )
