# ScholarOS Architecture Reference

This document is the authoritative architectural reference for **ScholarOS**. It provides an exhaustive, subsystem-by-subsystem breakdown of the design, contracts, interfaces, and operational flow across the 17 core subsystems.

---

## Subsystem Index

1. [Core & Kernel](#1-core--kernel)
2. [Dependency Injection (DI)](#2-dependency-injection-di)
3. [AI & Model Providers](#3-ai--model-providers)
4. [Knowledge Management](#4-knowledge-management)
5. [Embeddings & Vector Store](#5-embeddings--vector-store)
6. [Retrieval Subsystem](#6-retrieval-subsystem)
7. [Retrieval-Augmented Generation (RAG)](#7-retrieval-augmented-generation-rag)
8. [Research Engine](#8-research-engine)
9. [Memory Subsystem](#9-memory-subsystem)
10. [Tools Subsystem](#10-tools-subsystem)
11. [Plugins Subsystem](#11-plugins-subsystem)
12. [GUI & Desktop Application](#12-gui--desktop-application)
13. [Services Subsystem](#13-services-subsystem)
14. [Events & EventBus](#14-events--eventbus)
15. [Configuration Subsystem](#15-configuration-subsystem)
16. [Security Subsystem](#16-security-subsystem)
17. [Observability & Telemetry](#17-observability--telemetry)

---

## 1. Core & Kernel
- **Location**: `scholaros.core`, `scholaros.kernel`
- **Purpose**: Provides the minimal microkernel foundation and component lifecycle state machine.
- **Key Concepts**:
  - `Kernel`: Coordinates startup, service registration, state validation, and graceful teardown.
  - `Component`: Abstract base class representing any lifecycle-managed building block (`initialize()`, `start()`, `stop()`).
  - `LifecycleState`: State machine tracking states (`INITIALIZED`, `STARTING`, `RUNNING`, `STOPPING`, `STOPPED`, `FAILED`).
- **Design Rule**: The Core has zero external domain dependencies; it never references AI, GUI, or database layers.

---

## 2. Dependency Injection (DI)
- **Location**: `scholaros.container`
- **Purpose**: Manages runtime dependency resolution without magic, global singletons, or metaclass reflection.
- **Key Concepts**:
  - `Container`: Registry mapping contract types to concrete instances or factory providers.
  - `add_instance(interface, instance)`: Registers an existing instance.
  - `add_factory(interface, factory)`: Registers a lazy instantiation callable.
  - `resolve(interface)`: Type-safe lookup of services; raises `DependencyNotFoundError` on failure.

---

## 3. AI & Model Providers
- **Location**: `scholaros.ai`
- **Purpose**: Unified interface for local and cloud large language models.
- **Key Concepts**:
  - `AIClient`: High-level entrypoint for text generation, streaming, and prompt execution.
  - `AIManager`: Coordinates registered providers, routes model requests, and enforces timeouts.
  - `AIFactory`: Factory creating pre-configured clients and provider instances.
  - `AIProvider`: Base contract implemented by `OllamaProvider`, `OpenAIProvider`, `AnthropicProvider`, `GoogleProvider`, `OpenRouterProvider`, and `MockProvider`.
  - `PromptCatalog` & `PromptTemplate`: Manages parameterized system prompts and guardrails.

---

## 4. Knowledge Management
- **Location**: `scholaros.knowledge`
- **Purpose**: Ingests, normalizes, sanitizes, and organizes scientific research documents.
- **Key Concepts**:
  - `KnowledgeManager`: Coordinates collections and document ingestion.
  - `KnowledgeDocument`: Structured model encapsulating content, metadata (authors, year, doi), and chunk list.
  - Adapters: `PDFAdapter`, `MarkdownAdapter`, `TextAdapter`, `JSONAdapter` for format-specific parsing.
  - Chunking Engine: Segments long texts using sliding windows with configurable `chunk_size` and `chunk_overlap`.

---

## 5. Embeddings & Vector Store
- **Location**: `scholaros.embeddings`
- **Purpose**: Generates semantic embeddings and performs high-speed nearest neighbor search.
- **Key Concepts**:
  - `Embedding`: Encapsulates a float vector with memoized `norm` and reciprocal norm `inv_norm = (1.0 / norm)`.
  - `InMemoryVectorStore`: Thread-safe in-memory vector storage with RLock synchronization.
  - **$O(N \log k)$ Heap-Based Search**: Uses `heapq.nlargest` to avoid sorting entire vector collections.
  - **Fast Cosine Scoring**: Evaluates dot products scaled by precomputed inverse norms:
    $$\text{Cosine Similarity} = (\vec{q} \cdot \vec{d}) \times \frac{1}{\|\vec{d}\|}$$

---

## 6. Retrieval Subsystem
- **Location**: `scholaros.retrieval`
- **Purpose**: High-precision academic passage retrieval combining dense and sparse search.
- **Key Concepts**:
  - `RetrievalPipeline`: Coordinates querying, strategy execution, filtering, and scoring.
  - `HybridRetriever`: Combines keyword retrieval and vector search via Reciprocal Rank Fusion (RRF).
  - `RetrievalCache`: Thread-safe LRU cache with TTL expiration achieving **sub-millisecond (<0.5ms)** hits.
  - Scorer & Ranker: Applies minimum score thresholds (`min_score`) and normalizes confidence values.

---

## 7. Retrieval-Augmented Generation (RAG)
- **Location**: `scholaros.knowledge.rag`
- **Purpose**: Synthesizes verified research answers by grounding LLM generation in retrieved documents.
- **Key Concepts**:
  - `RAGPipeline`: Coordinates query formulation, retrieval execution, context assembly, and synthesis.
  - `RAGRequest`: Encapsulates user query, collection filters, strategy overrides, and token limits.
  - `RAGResponse`: Contains synthesized answer, source citations, context passages, and retrieval metrics.
  - `RAGService`: Exposes RAG capabilities to agents and application layers via DI.

---

## 8. Research Engine
- **Location**: `scholaros.research`
- **Purpose**: Executes multi-stage scientific research workflows.
- **Key Concepts**:
  - `ResearchSession`: State container preserving query history, plans, tasks, and reports.
  - `ResearchPlanner`: Decomposes academic questions into actionable research tasks (`ResearchTask`).
  - `ResearchWorkflowEngine`: Multi-stage state machine (Planning -> Retrieval -> Synthesis -> Citations).
  - `CitationManager`: Resolves academic references, tracks co-citations, and compiles bibliographies.
  - `ResearchReport`: Formatted report output with executive summary, detailed findings, and citations.

---

## 9. Memory Subsystem
- **Location**: `scholaros.memory`
- **Purpose**: Maintains conversational context and long-term research memory across sessions.
- **Key Concepts**:
  - `MemoryManager`: Coordinates short-term working memory and long-term associative memory.
  - `MemoryEntry`: Structured datum with timestamp, importance score, and tags.
  - `MemoryCollection`: Categorized memory containers (e.g. user preferences, past query insights).

---

## 10. Tools Subsystem
- **Location**: `scholaros.tools`
- **Purpose**: Extensible computational tools for agents and researchers.
- **Key Concepts**:
  - `Tool`: Abstract base class declaring execution contracts and parameter schemas.
  - `ToolRegistry`: Typed registry of available computational tools.
  - `ToolManifest`: Declares tool capabilities, arguments, and required security permissions.

---

## 11. Plugins Subsystem
- **Location**: `scholaros.plugins`
- **Purpose**: Sandboxed plugin architecture for third-party extensibility.
- **Key Concepts**:
  - `BasePlugin`: Lifecycle contract for external modules (`on_initialize`, `on_start`, `on_stop`).
  - `PluginManifest`: Declares plugin identity, author, version, and requested permissions.
  - `PermissionSet`: Explicit capability gates (`NETWORK`, `FILESYSTEM_READ`, `FILESYSTEM_WRITE`, `EXECUTION`).
  - `PluginSandbox`: Protects core application from unauthorized file or network access.

---

## 12. GUI & Desktop Application
- **Location**: `scholaros.gui`, `scholaros.applications`
- **Purpose**: Modern, responsive desktop user interface.
- **Key Concepts**:
  - `GUIApplication`: Central application controller managing UI state and services.
  - **Asynchronous Execution ThreadPool**: Background worker threads handle LLM generation and document ingestion without freezing the main Tkinter thread.
  - Views: `HomeView`, `ChatView`, `ResearchView`, `LibraryView`, `PluginView`, `SettingsView`.
  - Windows Launchers: Console launcher (`scholaros-gui`) and zero-console launcher (`scholaros-desktop` via `pythonw.exe`).

---

## 13. Services Subsystem
- **Location**: `scholaros.services`
- **Purpose**: Manages system services, capabilities, health checks, and lifecycle states.
- **Key Concepts**:
  - `Service`: Base contract for all background services (`initialize()`, `start()`, `stop()`, `health()`).
  - `ServiceHealth`: Health status reporting (`HEALTHY`, `DEGRADED`, `UNHEALTHY`, `UNKNOWN`) with diagnostics metrics.
  - `ServiceManager`: Discovers, starts, and supervises service dependencies topologically.

---

## 14. Events & EventBus
- **Location**: `scholaros.events`
- **Purpose**: Decoupled, asynchronous publish/subscribe communication between subsystems.
- **Key Concepts**:
  - `EventBus`: Central bus supporting synchronous and asynchronous dispatch.
  - `Event`: Strongly-typed event base class with execution IDs, timestamps, and payloads.
  - Typed Handlers: Subsystems subscribe to specific event classes without cross-coupling.

---

## 15. Configuration Subsystem
- **Location**: `scholaros.config`, `scholaros.platform`
- **Purpose**: Production configuration loading, schema validation, persistence, and OS path resolution.
- **Key Concepts**:
  - `ConfigurationManager`: Loads and validates `config.toml` with default fallback.
  - `scholaros.platform.paths`: Resolves platform-standard directories:
    - Windows: `%APPDATA%\ScholarOS\config`, `%LOCALAPPDATA%\ScholarOS\{data,cache,logs}`
    - Linux: XDG Base Directory specification compliance
    - macOS: Apple Application Support conventions
  - Environment overrides (`SCHOLAROS_HOME`, etc.) for seamless testing.

---

## 16. Security Subsystem
- **Location**: `scholaros.security`
- **Purpose**: Hardened defense against prompt injection, path traversal, and unauthorized plugin actions.
- **Key Concepts**:
  - `PathSanitizer`: Validates document import paths to prevent directory traversal (`../`).
  - `RAGSecurity`: Isolates retrieved document excerpts to mitigate indirect prompt injection attacks.
  - `PluginSecurity`: Enforces capability permissions before granting network or filesystem access.

---

## 17. Observability & Telemetry
- **Location**: `scholaros.observability`, `scholaros.logging`
- **Purpose**: Production-grade diagnostics, execution tracing, and structured logging.
- **Key Concepts**:
  - `StructuredLogger`: Emits JSON-formatted log lines with trace IDs, component tags, and timestamps.
  - `TelemetryCollector`: Gathers RAG latency, retrieval scores, and provider response times.
  - Diagnostics Tracing: Enables full query-to-response audit trails:
    $$\text{Query} \to \text{Strategy} \to \text{Retrieved Chunks} \to \text{Scores} \to \text{Prompt} \to \text{Model} \to \text{Response}$$

Next Step: View visual sequence and component diagrams in the [Architecture Diagrams Guide](diagrams.md).
