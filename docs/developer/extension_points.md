# Extension Points & Hook Subsystem

ScholarOS provides declarative extension mechanisms allowing internal subsystems and third-party integrations to hook into system lifecycle events, request pipelines, and UI interactions.

---

## 1. The Hook Subsystem (`scholaros.hooks`)

ScholarOS includes a priority-ordered hook execution system (`HookManager`):

```python
from scholaros.hooks.manager import HookManager
from scholaros.hooks.hook import Hook

manager = HookManager()

# Define a hook callback
def on_document_ingested(payload: dict) -> None:
    print(f"Ingested document: {payload['title']}")

# Register hook with priority (lower number = higher priority)
manager.register_hook(
    name="on_document_ingested",
    callback=on_document_ingested,
    priority=10,
)

# Execute hook across all registered callbacks
manager.execute_hook("on_document_ingested", payload={"title": "Attention Is All You Need"})
```

---

## 2. EventBus Domain Events (`scholaros.events`)

For decoupled asynchronous notifications, subsystems publish and subscribe to strongly-typed events via `EventBus`:

```python
from scholaros.events.bus import EventBus
from scholaros.research.events import ResearchCompleted

bus = EventBus()

def on_research_finished(event: ResearchCompleted) -> None:
    print(f"Research finished for query: '{event.query}' in {event.duration:.2f}s")

# Subscribe to event type
bus.subscribe(ResearchCompleted, on_research_finished)
```

### Standard Event Categories
- `scholaros.core.events`: Kernel startup, shutdown, component failure.
- `scholaros.ai.events`: Prompt generated, streaming token emitted, provider error.
- `scholaros.research.events`: `ResearchStarted`, `ResearchStageStarted`, `ResearchCompleted`, `ResearchFailed`.
- `scholaros.knowledge.rag.events`: `RAGRetrievalStarted`, `RAGRetrievalCompleted`, `RAGGenerated`.

---

## 3. Custom Service Registration

You can inject custom services into the microkernel via the Dependency Injection container:

```python
from scholaros.services.service import Service
from scholaros.services.metadata import ServiceMetadata
from scholaros.container.container import Container

class CitationAnalysisService(Service):
    def __init__(self) -> None:
        super().__init__(
            metadata=ServiceMetadata(
                name="CitationAnalysisService",
                version="1.0.0",
                capabilities=("graph_analysis", "co_citation"),
            )
        )

# Register into container
container = Container()
service = CitationAnalysisService()
container.add_instance(CitationAnalysisService, service)
```

Next Step: Learn how to author sandboxed plugins in the [Plugin Development Guide](plugin_development.md).
