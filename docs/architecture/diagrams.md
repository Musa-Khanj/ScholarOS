# Architectural Flowcharts & Sequence Diagrams

This document illustrates the execution lifecycles, data flows, and subsystem interactions within ScholarOS using Mermaid diagrams.

---

## 1. System Boot & DI Container Wiring Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Main as Main Launcher (CLI/GUI)
    participant Platform as Platform Paths
    participant Config as ConfigurationManager
    participant Kernel as Microkernel
    participant Container as DI Container
    participant Services as ServiceManager
    participant EventBus as EventBus

    Main->>Platform: Resolve OS directories (App, Config, Data)
    Main->>Config: Load & validate config.toml
    Main->>Kernel: kernel.boot()
    Kernel->>Container: Initialize Container
    Kernel->>EventBus: Instantiate central EventBus
    Kernel->>Services: Register Built-in Services
    Note over Services,Container: Services (AI, Knowledge, RAG, Research) register into Container
    Kernel->>Services: Start services in topological dependency order
    Kernel-->>Main: Kernel in RUNNING state
```

---

## 2. End-to-End RAG Research Execution Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant App as GUIApplication / CLI
    participant Worker as Background ThreadPool
    participant Pipeline as ResearchPipeline
    participant RAG as RAGService
    participant Cache as RetrievalCache
    participant Retriever as HybridRetriever
    participant VectorStore as InMemoryVectorStore
    participant AI as AIClient / Ollama

    User->>App: Submit Research Query
    App->>Worker: Dispatch research_async(query)
    Note over App: GUI remains responsive & interactive
    Worker->>Pipeline: execute_rag(query)
    Pipeline->>RAG: generate_response(query)
    RAG->>Cache: Check query cache key
    alt Cache Hit (<0.5ms)
        Cache-->>RAG: Cached matching passages
    else Cache Miss
        RAG->>Retriever: retrieve(query, limit=10, min_score=0.35)
        Retriever->>VectorStore: top_k cosine search (heap O(N log k))
        VectorStore-->>Retriever: dense vector results
        Retriever-->>RAG: ranked document passages
        RAG->>Cache: commit to LRU cache
    end
    RAG->>AI: generate(prompt_with_grounded_context)
    AI-->>RAG: Synthesized academic response
    RAG-->>Pipeline: ResearchResult (text, citations, metrics)
    Pipeline-->>Worker: Completed result
    Worker->>App: Callback on UI thread
    App-->>User: Display answer with citations and metrics
```

---

## 3. Asynchronous GUI Execution Model

```mermaid
flowchart TD
    subgraph UIThread ["Tkinter Main UI Thread"]
        EventLoop["Tkinter MainLoop (60 FPS)"]
        UserAction["User Click: 'Start Research'"]
        Spinner["Show Progress Indicator"]
        Render["Render Results View"]
        
        UserAction --> EventLoop
        EventLoop --> Spinner
    end

    subgraph ThreadPool ["ThreadPoolExecutor (Background Workers)"]
        TaskQueue["Worker Queue"]
        Worker1["Worker Thread 1\n(Inference / Generation)"]
        Worker2["Worker Thread 2\n(Document Ingestion)"]
        
        TaskQueue --> Worker1
        TaskQueue --> Worker2
    end

    EventLoop -->|dispatch execute_async| TaskQueue
    Worker1 -->|root.after callback| Render
    Worker2 -->|root.after callback| Render
```

---

## 4. Diagnostics & Telemetry Tracing Flow

```mermaid
flowchart LR
    subgraph ExecutionTrace ["Query Trace Pipeline"]
        Q[Query] --> S[Strategy Decision]
        S --> R[Retrieved Chunks]
        R --> Sc[Score Normalization]
        Sc --> C[Assembled Context]
        C --> P[Prompt Template]
        P --> M[Model Invocation]
        M --> Res[Final Response]
    end

    subgraph TelemetrySink ["Observability Subsystem"]
        Logger["Structured JSON Logger\n(scholaros.log)"]
        Bus["EventBus Metrics\n(Latency, Token Usage)"]
    end

    ExecutionTrace --> Logger
    ExecutionTrace --> Bus
```
