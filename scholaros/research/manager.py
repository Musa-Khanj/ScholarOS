"""
ScholarOS
Research Session Manager

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Manager for
research sessions.
"""

from typing import TYPE_CHECKING, Any
from uuid import uuid4

from scholaros.research.registry import (
    ResearchSessionRegistry,
)
from scholaros.research.session import (
    ResearchSession,
)

if TYPE_CHECKING:
    from scholaros.knowledge.manager import KnowledgeManager
    from scholaros.memory.manager import MemoryManager
    from scholaros.research.pipeline import ResearchPipeline
    from scholaros.research.result import ResearchResult


class ResearchSessionManager:
    """
    Manager for research sessions.

    Coordinates session lifecycle, conversation working memory,
    research execution, persistent memory, and knowledge export.
    """

    def __init__(
        self,
        registry: ResearchSessionRegistry | None = None,
        memory_manager: MemoryManager | None = None,
        knowledge_manager: KnowledgeManager | None = None,
        pipeline: ResearchPipeline | None = None,
    ) -> None:
        """
        Initialize the session manager.
        """
        self._registry = registry if registry is not None else ResearchSessionRegistry()
        self._memory_manager = memory_manager
        self._knowledge_manager = knowledge_manager
        self._pipeline = pipeline
        self._active_session_id: str | None = None

    @property
    def memory_manager(self) -> MemoryManager | None:
        """Return the attached memory manager."""
        return self._memory_manager

    @property
    def knowledge_manager(self) -> KnowledgeManager | None:
        """Return the attached knowledge manager."""
        return self._knowledge_manager

    @property
    def pipeline(self) -> ResearchPipeline | None:
        """Return the attached research pipeline."""
        return self._pipeline

    @pipeline.setter
    def pipeline(self, value: ResearchPipeline | None) -> None:
        self._pipeline = value

    @property
    def active_session_id(self) -> str | None:
        """Return the ID of the active session."""
        return self._active_session_id

    @active_session_id.setter
    def active_session_id(self, value: str | None) -> None:
        self._active_session_id = value

    @property
    def active_session(self) -> ResearchSession | None:
        """Return the active session if available, or the most recent session."""
        if self._active_session_id:
            s = self.get(self._active_session_id)
            if s:
                return s
        all_s = self.sessions()
        return all_s[-1] if all_s else None

    @property
    def registry(
        self,
    ) -> ResearchSessionRegistry:
        """
        Return the
        session registry.
        """

        return self._registry

    def get(self, session_id: str) -> ResearchSession | None:
        """Return a session by ID."""
        for s in self.sessions():
            if s.id == session_id:
                return s
        return None

    def create(
        self,
        query: str = "",
        title: str = "",
    ) -> ResearchSession:
        """
        Create and register
        a research session.
        """

        session = ResearchSession(
            query=query,
            title=title,
        )

        self.register(
            session,
        )
        self._active_session_id = session.id

        return session


    def register(
        self,
        session: ResearchSession,
    ) -> None:
        """
        Register a
        research session.
        """

        self._registry.register(
            session,
        )

    def unregister(
        self,
        session: ResearchSession,
    ) -> None:
        """
        Unregister a
        research session.
        """

        self._registry.unregister(
            session,
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all
        research sessions.
        """

        self._registry.clear()

    def sessions(
        self,
    ) -> list[
        ResearchSession
    ]:
        """
        Return all
        research sessions.
        """

        return (
            self._registry.sessions()
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number
        of sessions.
        """

        return len(
            self._registry,
        )

    def __iter__(
        self,
    ):
        """
        Iterate over the
        research sessions.
        """

        return iter(
            self._registry,
        )

    def __contains__(
        self,
        session: ResearchSession,
    ) -> bool:
        """
        Return whether the
        session is managed.
        """

        return (
            session
            in self._registry
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"size={len(self)}"
            f")"
        )

    def run_research(
        self,
        query: str,
        session_id: str | None = None,
        use_workflow: bool = True,
        publish_to_knowledge: bool = False,
        notes: list[str] | None = None,
        **kwargs: Any,
    ) -> ResearchResult:
        """
        Execute research in the context of an active or specified session,
        incorporating prior session context and persisting results to memory.
        """
        from scholaros.research.exceptions import ResearchExecutionError

        if self._pipeline is None:
            raise ResearchExecutionError(
                "ResearchSessionManager has no configured ResearchPipeline."
            )

        # 1. Resolve target session
        session: ResearchSession | None = None
        if session_id:
            session = self.get(session_id)
        if session is None:
            session = self.active_session
        if session is None:
            session = self.create(query=query)

        self._active_session_id = session.id

        # 2. Extract conversation context
        session_context = session.get_conversation_context()

        # 3. Execute research
        initial_data = kwargs.pop("initial_data", None)
        init_dict: dict[str, Any] = dict(initial_data) if initial_data else {}
        if session_context:
            init_dict["session_context"] = session_context
        init_dict["session_id"] = session.id

        if use_workflow and hasattr(self._pipeline, "execute_workflow"):
            result = self._pipeline.execute_workflow(
                query=query,
                initial_data=init_dict,
                **kwargs,
            )
        else:
            result = self._pipeline.execute_rag(
                query=query,
                **kwargs,
            )

        # 4. Record interaction in session
        session.record_interaction(query=query, result=result, notes=notes)

        # 5. Persist to MemoryManager
        if self._memory_manager is not None:
            self._persist_to_memory(session, query, result)

        # 6. Publish to KnowledgeManager if requested
        if publish_to_knowledge and self._knowledge_manager is not None:
            doc = session.to_knowledge_document()
            self._knowledge_manager.add_document(doc, collection_name="research_notes")

        return result

    def _persist_to_memory(
        self, session: ResearchSession, query: str, result: ResearchResult
    ) -> None:
        """Record session interaction and research findings into MemoryManager."""
        if self._memory_manager is None:
            return
        try:
            from scholaros.memory.collection import MemoryCollection
            from scholaros.memory.entry import MemoryEntry

            # 1. Session conversation history collection
            session_col = self._memory_manager.get("session_history")
            if session_col is None:
                session_col = MemoryCollection()
                self._memory_manager.register("session_history", session_col)

            session_col.add(
                MemoryEntry(
                    entry_id=str(uuid4()),
                    content=f"Session {session.id} Turn: Q: {query}\nA: {result.content[:500]}",
                    metadata={
                        "session_id": session.id,
                        "query": query,
                        "model": result.model,
                        "sources_count": len(result.sources),
                    },
                )
            )

            # 2. Research findings memory collection
            research_col = self._memory_manager.get("research_history")
            if research_col is None:
                research_col = MemoryCollection()
                self._memory_manager.register("research_history", research_col)

            research_col.add(
                MemoryEntry(
                    entry_id=str(uuid4()),
                    content=f"Research Findings: {query}\nSynthesis: {result.content[:500]}",
                    metadata={
                        "session_id": session.id,
                        "query": query,
                        "has_workflow": result.has_workflow,
                    },
                )
            )
        except Exception:
            pass