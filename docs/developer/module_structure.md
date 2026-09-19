# Module Structure & Package Organization

This guide provides a comprehensive map of the packages in `scholaros/`.

---

## 1. Directory Tree

```text
scholaros/
├── agents/             # Autonomous agent abstractions (ResearchAgent, BaseAgent)
├── ai/                 # LLM client, providers (Ollama, OpenAI, Anthropic, Google, Mock), prompts
├── applications/       # High-level application controller, lifecycle management
├── bootstrap/          # System bootstrapping and initialization sequences
├── cli/                # Command-line interface parser, main dispatcher, and subcommands
├── collaboration/      # Multi-agent coordination protocols and shared memory
├── config/             # TOML configuration loading, schema validation, persistence
├── container/          # Lightweight Dependency Injection (DI) container
├── contracts/          # Base interfaces, abstract classes, and protocol definitions
├── core/               # Microkernel foundations, component lifecycle, base exceptions
├── dependency/         # Dependency resolution graph and topological sorter
├── embeddings/         # Dense vector embedding abstractions and in-memory vector store
├── events/             # Asynchronous EventBus and typed domain events
├── execution/          # Task and workflow execution engine
├── extensions/         # System extension registry and loader
├── gui/                # Desktop Tkinter user interface (Window, Views, Components, Theme)
├── hooks/              # Priority-ordered hook manager and lifecycle interceptors
├── kernel/             # Microkernel bootstrapper and subsystem orchestrator
├── knowledge/          # Knowledge base, document adapters (PDF, TXT, MD, JSON), chunking, RAG
├── lifecycle/          # Lifecycle state machine (INITIALIZED, STARTING, RUNNING, STOPPING)
├── logging/            # Logging service, formatters, and rotating file handlers
├── memory/             # Short-term and long-term agent memory management
├── observability/      # Structured JSON logging, telemetry metrics, and tracing
├── planner/            # Research query decomposition and planning
├── platform/           # OS-specific directory resolution (Windows, Linux, macOS)
├── plugins/            # Sandboxed plugin system, capability permissions, manifests
├── registry/           # Generic typed registry abstraction
├── research/           # Research sessions, citations, reports, and workflow engine
├── retrieval/          # Hybrid retrieval engine (keyword, semantic, RRF, rankers, cache)
├── runtime/            # Runtime context, execution environments
├── scheduler/          # Task queue, scheduler, and background worker threads
├── security/           # Path sanitization, prompt injection defense, plugin permissions
├── services/           # Service descriptors, health checks, service registry
├── tools/              # Computational tools, manifests, and execution harness
├── ui/                 # Legacy UI integration bridge
└── workflow/           # State machines and execution graphs
```

---

## 2. Key Subsystem Highlights

### `scholaros.core` & `scholaros.kernel`
Contains `Kernel`, `Microkernel`, `Component`, and `Lifecycle`. Provides the foundational boot sequence and coordinates subsystem lifecycle transitions.

### `scholaros.ai`
Houses `AIClient`, `AIManager`, `AIFactory`, and concrete provider integrations (`OllamaProvider`, `OpenAIProvider`, `AnthropicProvider`, `GoogleProvider`, `OpenRouterProvider`, `MockProvider`).

### `scholaros.knowledge` & `scholaros.retrieval`
- `knowledge`: Ingests documents using format-specific adapters (`PDFAdapter`, `MarkdownAdapter`, `TextAdapter`, `JSONAdapter`).
- `retrieval`: Orchestrates keyword search, dense vector cosine similarity, Reciprocal Rank Fusion (`HybridRetriever`), and thread-safe LRU caching (`RetrievalCache`).

### `scholaros.research`
Implements autonomous literature synthesis: decomposes a research query into tasks (`ResearchTask`), executes retrieval, synthesizes structured findings, generates citations (`CitationManager`), and compiles reports (`ResearchReport`).

### `scholaros.gui`
Modern, responsive desktop interface constructed in pure Python Tkinter/ttk:
- Asynchronous worker dispatch (`execute_async`) prevents UI blocking.
- Structured views: Home, AI Chat, Research, Knowledge Library, Plugins, Settings.

Next Step: Learn how to intercept system lifecycle events in the [Extension Points Guide](extension_points.md).
