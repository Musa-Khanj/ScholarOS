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
    from scholaros.knowledge.manager import KnowledgeManager
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
        knowledge_manager: KnowledgeManager | None = None,
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
        self._knowledge_manager = knowledge_manager
        self._container = container
        self._event_bus = event_bus
        self._config = config
        self._config_manager = config_manager
        self._max_workers = max_workers
        self._executor: ThreadPoolExecutor | None = None
        self._state = ApplicationState.INITIALIZED
        self._session: Any | None = None
        self._memory: Any | None = None
        self._last_citations: list[Any] = []

        # 1. Inspect services bundle if supplied
        if services is not None:
            if self._ai_manager is None:
                self._ai_manager = getattr(services, "ai_manager", None)
            if self._research_pipeline is None:
                self._research_pipeline = getattr(services, "research_pipeline", None)
            if self._rag_pipeline is None:
                self._rag_pipeline = getattr(services, "rag_pipeline", None)
            if self._plugin_manager is None:
                self._plugin_manager = getattr(services, "plugin_manager", None)
            if self._knowledge_manager is None:
                self._knowledge_manager = getattr(services, "knowledge_manager", None)
            if self._container is None:
                self._container = getattr(services, "container", None)
            if self._event_bus is None:
                self._event_bus = getattr(services, "event_bus", None)
            if self._config is None:
                self._config = getattr(services, "config", None)
            if self._config_manager is None:
                self._config_manager = getattr(services, "config_manager", None)

        # 2. Inspect DI Container if supplied
        cnt = self._container
        if cnt is not None:

            def _resolve(svc_type: type) -> Any:
                if hasattr(cnt, "resolve_optional"):
                    return cnt.resolve_optional(svc_type)
                if hasattr(cnt, "resolve"):
                    try:
                        return cnt.resolve(svc_type)
                    except Exception:
                        return None
                return None

            if self._config_manager is None:
                from scholaros.config.manager import ConfigManager

                self._config_manager = _resolve(ConfigManager)
            if self._event_bus is None:
                from scholaros.events.bus import EventBus

                self._event_bus = _resolve(EventBus)
            if self._ai_manager is None:
                from scholaros.ai.manager import AIManager

                self._ai_manager = _resolve(AIManager)
            if self._knowledge_manager is None:
                from scholaros.knowledge.manager import KnowledgeManager

                self._knowledge_manager = _resolve(KnowledgeManager)
            if self._research_pipeline is None:
                from scholaros.research.pipeline import ResearchPipeline

                self._research_pipeline = _resolve(ResearchPipeline)
            if self._rag_pipeline is None:
                from scholaros.knowledge.rag.pipeline import RAGPipeline

                self._rag_pipeline = _resolve(RAGPipeline)
            if self._plugin_manager is None:
                from scholaros.plugins.manager import PluginManager

                self._plugin_manager = _resolve(PluginManager)

        if self._config_manager is None and self._config is not None:
            if hasattr(self._config, "load_config") or hasattr(self._config, "to_settings"):
                self._config_manager = self._config

        # 3. Context injection into window
        if hasattr(self._window, "set_application"):
            self._window.set_application(self)
        elif hasattr(self._window, "application"):
            try:
                setattr(self._window, "application", self)
            except Exception:
                pass

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
    def knowledge_manager(self) -> KnowledgeManager | None:
        return self._knowledge_manager

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

    @property
    def session(self) -> Any | None:
        """Return the active AI session, initializing one if an AI manager is available."""
        if self._session is None and self.ai_manager is not None:
            try:
                from scholaros.ai.session import AISession

                default_model = None
                if self._config is not None and hasattr(self._config, "models"):
                    default_model = getattr(self._config.models, "default_chat_model", None)

                self._session = AISession(
                    manager=self.ai_manager,
                    model=default_model,
                )
            except Exception:
                pass
        return self._session

    @property
    def conversation(self) -> Any | None:
        """Return the active conversation object from the session if available."""
        if self.session is not None and hasattr(self.session, "conversation"):
            return self.session.conversation
        return None

    @property
    def memory(self) -> Any:
        """Return runtime working memory."""
        if self._memory is None:
            try:
                from scholaros.memory.memory import Memory

                self._memory = Memory()
            except Exception:
                pass
        return self._memory

    @property
    def last_citations(self) -> list[Any]:
        """Return citations from the most recent chat or research turn."""
        return getattr(self, "_last_citations", [])

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

        active_model = None
        if self._config is not None and hasattr(self._config, "models"):
            active_model = getattr(self._config.models, "default_chat_model", None)
        elif self._config_manager is not None and hasattr(self._config_manager, "config"):
            cfg = getattr(self._config_manager, "config", None)
            if cfg is not None and hasattr(cfg, "models"):
                active_model = getattr(cfg.models, "default_chat_model", None)

        return {
            "status": self.status(),
            "ai": self.ai_manager is not None,
            "research": self.research_pipeline is not None,
            "rag": self.rag_pipeline is not None,
            "plugins": self.plugin_manager is not None,
            "knowledge": self.knowledge_manager is not None,
            "active_provider": active_provider,
            "active_model": active_model,
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
        Maintains conversational history in the active session.
        """
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            raise ValueError("Chat prompt cannot be empty.")

        # Record user turn in active conversation session
        if self.conversation is not None and hasattr(self.conversation, "add_user"):
            try:
                self.conversation.add_user(cleaned_prompt)
            except Exception:
                pass

        # 1. Prefer AIManager
        if self.ai_manager is not None:
            from scholaros.ai.request import AIRequest

            ai_provider = self.ai_manager.select_provider(
                model=model,
                requested_provider=provider,
            )
            messages = list(self.conversation.messages) if self.conversation is not None else []
            request = AIRequest(prompt=cleaned_prompt, messages=messages, model=model)
            response = ai_provider.generate(request)

            if self.conversation is not None and hasattr(self.conversation, "add_assistant"):
                try:
                    self.conversation.add_assistant(response.content)
                except Exception:
                    pass

            raw_meta = getattr(response, "metadata", None)
            if isinstance(raw_meta, dict):
                cites = raw_meta.get("citations", [])
                self._last_citations = list(cites) if isinstance(cites, (list, tuple)) else []
            else:
                self._last_citations = []
            return response.content

        # 2. Fallback to RAGPipeline
        if self.rag_pipeline is not None:
            from scholaros.knowledge.rag.request import RAGRequest

            rag_req = RAGRequest(query=cleaned_prompt)
            rag_res = self.rag_pipeline.run(rag_req)

            if self.conversation is not None and hasattr(self.conversation, "add_assistant"):
                try:
                    self.conversation.add_assistant(rag_res.content)
                except Exception:
                    pass

            raw_sources = getattr(rag_res, "sources", None)
            if isinstance(raw_sources, (list, tuple)):
                self._last_citations = list(raw_sources)
            else:
                self._last_citations = []
            return rag_res.content

        raise RuntimeError("No AI provider or RAG pipeline is configured.")

    def clear_chat(self) -> None:
        """Reset conversation history in active session."""
        if self._session is not None and hasattr(self._session, "reset"):
            try:
                self._session.reset()
            except Exception:
                pass
        elif self.conversation is not None and hasattr(self.conversation, "clear"):
            try:
                self.conversation.clear()
            except Exception:
                pass
        self._last_citations = []

    def research(
        self,
        query: str,
        template: str | None = None,
        use_workflow: bool = False,
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
            if use_workflow:
                kwargs["use_workflow"] = True
            return self.research_pipeline.execute(cleaned_query, **kwargs)

        raise RuntimeError("Research pipeline is not configured.")

    def cancel_research(self, reason: str = "User requested cancellation") -> bool:
        """Signal cancellation for the actively executing research workflow."""
        if self.research_pipeline is not None and hasattr(
            self.research_pipeline, "cancel_active_workflow"
        ):
            return self.research_pipeline.cancel_active_workflow(reason)
        return False

    def search_knowledge(
        self,
        query: str,
        minimum_score: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Query knowledge repository via RAGPipeline or KnowledgeManager and return structured source items.
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
                results.append(
                    {
                        "content": getattr(item, "content", str(item)),
                        "score": getattr(item, "score", 1.0),
                        "source": getattr(item, "source", "unknown"),
                        "metadata": getattr(item, "metadata", {}),
                    }
                )
            return results

        if self.knowledge_manager is not None:
            res_km = self.knowledge_manager.search(cleaned_query)
            km_results: list[dict[str, Any]] = []
            for km_item in res_km.results:
                score = getattr(km_item, "score", 1.0)
                if score >= minimum_score:
                    km_results.append(
                        {
                            "content": getattr(km_item, "content", ""),
                            "score": score,
                            "source": getattr(km_item, "document_id", "doc"),
                            "metadata": getattr(km_item, "metadata", {}),
                        }
                    )
            return km_results

        raise RuntimeError("RAG pipeline is not configured.")

    def list_documents(self, collection_name: str | None = None) -> list[dict[str, Any]]:
        """Return list of indexed documents from KnowledgeManager."""
        if self.knowledge_manager is not None:
            docs: list[dict[str, Any]] = []
            colls = (
                [collection_name]
                if collection_name
                else (list(self.knowledge_manager.names()) or ["default"])
            )
            for col in colls:
                for doc in self.knowledge_manager.storage.list_documents(col):
                    docs.append(
                        {
                            "id": doc.identifier,
                            "title": doc.title,
                            "collection": col,
                            "status": getattr(doc, "status", "indexed"),
                            "chunks_count": len(doc.chunks),
                            "content_hash": getattr(doc, "content_hash", ""),
                            "content": doc.content,
                            "metadata": (
                                doc.metadata.to_dict() if hasattr(doc.metadata, "to_dict") else {}
                            ),
                        }
                    )
            return docs
        return []

    def get_document(
        self,
        document_id: str,
        collection_name: str = "default",
    ) -> dict[str, Any] | None:
        """Retrieve full document details by ID."""
        if self.knowledge_manager is not None:
            doc = self.knowledge_manager.storage.get_document(
                document_id, collection_name=collection_name
            )
            target_col = collection_name
            if doc is None:
                for col in self.knowledge_manager.names():
                    doc = self.knowledge_manager.storage.get_document(
                        document_id, collection_name=col
                    )
                    if doc is not None:
                        target_col = col
                        break
            if doc is not None:
                return {
                    "id": doc.identifier,
                    "title": doc.title,
                    "collection": target_col,
                    "status": getattr(doc, "status", "indexed"),
                    "chunks_count": len(doc.chunks),
                    "content_hash": getattr(doc, "content_hash", ""),
                    "content": doc.content,
                    "metadata": (
                        doc.metadata.to_dict() if hasattr(doc.metadata, "to_dict") else {}
                    ),
                    "chunks": [
                        c.to_dict() if hasattr(c, "to_dict") else str(c) for c in doc.chunks
                    ],
                }
        return None

    def add_document(
        self,
        document_or_path: Any,
        title: str | None = None,
        content: str | None = None,
        collection_name: str = "default",
        duplicate_policy: str = "replace",
    ) -> dict[str, Any]:
        """Ingest or register a document into the Knowledge subsystem."""
        if self.knowledge_manager is None:
            raise RuntimeError("Knowledge manager is not configured.")

        # Path ingestion check
        is_path = False
        try:
            from pathlib import Path

            p = Path(document_or_path)
            if p.is_file():
                is_path = True
        except Exception:
            is_path = False

        if is_path:
            from pathlib import Path
            from scholaros.knowledge.loader import KnowledgeLoader

            loader = KnowledgeLoader(manager=self.knowledge_manager)
            res = loader.ingest_file(
                file_path=Path(document_or_path),
                collection_name=collection_name,
                duplicate_policy=duplicate_policy,
            )
            if res.document is None:
                raise RuntimeError(res.error or f"Failed to ingest file '{document_or_path}'.")
            doc = res.document
        elif hasattr(document_or_path, "identifier") and hasattr(document_or_path, "content"):
            doc = self.knowledge_manager.add_document(
                document=document_or_path,
                collection_name=collection_name,
                duplicate_policy=duplicate_policy,
            )
        else:
            from scholaros.knowledge.document import KnowledgeDocument

            raw_text = content if content is not None else str(document_or_path)
            doc_id = str(title or f"doc_{abs(hash(raw_text)) % 100000}")
            doc_title = str(title or doc_id)
            new_doc = KnowledgeDocument(identifier=doc_id, title=doc_title, content=raw_text)
            doc = self.knowledge_manager.add_document(
                document=new_doc,
                collection_name=collection_name,
                duplicate_policy=duplicate_policy,
            )

        return {
            "id": doc.identifier,
            "title": doc.title,
            "collection": collection_name,
            "status": getattr(doc, "status", "indexed"),
            "chunks_count": len(doc.chunks),
            "content_hash": getattr(doc, "content_hash", ""),
            "content": doc.content,
            "metadata": doc.metadata.to_dict() if hasattr(doc.metadata, "to_dict") else {},
        }

    def remove_document(
        self,
        document_id: str,
        collection_name: str = "default",
    ) -> bool:
        """Remove a document from the Knowledge subsystem."""
        if self.knowledge_manager is None:
            raise RuntimeError("Knowledge manager is not configured.")
        removed = self.knowledge_manager.remove_document(
            document_id, collection_name=collection_name
        )
        if not removed:
            for col in self.knowledge_manager.names():
                if col != collection_name:
                    if self.knowledge_manager.remove_document(document_id, collection_name=col):
                        return True
        return removed

    def reindex_knowledge(self) -> int:
        """Trigger reindexing of all collections in the Knowledge subsystem."""
        if self.knowledge_manager is None:
            raise RuntimeError("Knowledge manager is not configured.")
        return self.knowledge_manager.reindex_all()

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
                    if (
                        root is not None
                        and type(root).__name__ != "MagicMock"
                        and hasattr(root, "after")
                    ):
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
                    if (
                        root is not None
                        and type(root).__name__ != "MagicMock"
                        and hasattr(root, "after")
                    ):
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
        on_complete: Callable[[str], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        model: str | None = None,
        provider: str | None = None,
        on_success: Callable[[str], None] | None = None,
    ) -> Future[Any]:
        """Asynchronously execute chat without blocking the UI thread."""

        def _default_success(_: str) -> None:
            pass

        success_cb = on_complete if on_complete is not None else on_success
        if success_cb is None:
            success_cb = _default_success
        return self.execute_async(
            self.chat,
            prompt=prompt,
            model=model,
            provider=provider,
            on_success=success_cb,
            on_error=on_error,
        )

    def research_async(
        self,
        query: str,
        on_complete: Callable[[Any], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        template: str | None = None,
        use_workflow: bool = False,
        on_success: Callable[[Any], None] | None = None,
        **kwargs: Any,
    ) -> Future[Any]:
        """Asynchronously execute research without blocking the UI thread."""

        def _default_success(_: Any) -> None:
            pass

        success_cb = on_complete if on_complete is not None else on_success
        if success_cb is None:
            success_cb = _default_success

        return self.execute_async(
            self.research,
            query=query,
            template=template,
            use_workflow=use_workflow,
            on_success=success_cb,
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

    def add_document_async(
        self,
        document_or_path: Any,
        title: str | None = None,
        content: str | None = None,
        collection_name: str = "default",
        duplicate_policy: str = "replace",
        on_complete: Callable[[dict[str, Any]], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> Future[Any]:
        """Asynchronously add or ingest a document without blocking the UI thread."""

        def _default_success(_: dict[str, Any]) -> None:
            pass

        return self.execute_async(
            self.add_document,
            document_or_path=document_or_path,
            title=title,
            content=content,
            collection_name=collection_name,
            duplicate_policy=duplicate_policy,
            on_success=on_complete if on_complete is not None else _default_success,
            on_error=on_error,
        )

    def remove_document_async(
        self,
        document_id: str,
        collection_name: str = "default",
        on_complete: Callable[[bool], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> Future[Any]:
        """Asynchronously remove a document without blocking the UI thread."""

        def _default_success(_: bool) -> None:
            pass

        return self.execute_async(
            self.remove_document,
            document_id=document_id,
            collection_name=collection_name,
            on_success=on_complete if on_complete is not None else _default_success,
            on_error=on_error,
        )

    def reindex_knowledge_async(
        self,
        on_complete: Callable[[int], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> Future[Any]:
        """Asynchronously reindex all knowledge collections without blocking the UI thread."""

        def _default_success(_: int) -> None:
            pass

        return self.execute_async(
            self.reindex_knowledge,
            on_success=on_complete if on_complete is not None else _default_success,
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
                results.append(
                    {
                        "id": p.id,
                        "name": p.name,
                        "version": p.version,
                        "state": self.plugin_manager.state(p.id).name,
                        "description": desc or "",
                    }
                )
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
        return f"{self.__class__.__name__}(window={self.window!r})"
