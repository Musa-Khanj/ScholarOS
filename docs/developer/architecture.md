# Subsystem Architecture & Dependency Inversion

ScholarOS is engineered according to a strict **Microkernel & Inversion of Control** architecture. This document explains the dependency flow, layer boundaries, and abstraction contracts.

---

## 1. The Four-Layer Architectural Model

```mermaid
flowchart TD
    subgraph L4 ["Layer 4: Presentation & Applications"]
        GUI["GUI Layer (Tkinter, Views, Components)"]
        CLI["CLI Layer (scholaros commands)"]
        AppController["ApplicationController / GUIApplication"]
        GUI --> AppController
        CLI --> AppController
    end

    subgraph L3 ["Layer 3: Domain Subsystems"]
        AI["AI Subsystem (Providers, Prompts, Client)"]
        Research["Research Subsystem (Sessions, Planner, Workflows)"]
        RAG["RAG Subsystem (Pipelines, Context, Scoring)"]
        Knowledge["Knowledge Subsystem (Documents, Collections, Adapters)"]
        Retrieval["Retrieval Subsystem (Keyword, Semantic, Hybrid RRF)"]
        Embeddings["Embeddings Subsystem (VectorStore, Heap Top-K)"]
        Memory["Memory Subsystem (Short/Long-term Storage)"]
        Plugins["Plugins Subsystem (Sandbox, Manifests, Permissions)"]
    end

    subgraph L2 ["Layer 2: Service Bus & Coordination"]
        Services["Service Container & Manager"]
        EventBus["EventBus (Publish/Subscribe, Diagnostics)"]
        Security["Security Subsystem (Sanitization, Injection Defense)"]
        Observability["Observability (Structured Logging, Telemetry)"]
        Config["Configuration & Settings"]
    end

    subgraph L1 ["Layer 1: Core / Microkernel"]
        Kernel["ScholarOS Microkernel"]
        DIContainer["Dependency Injection Container"]
        Contracts["Abstract Base Contracts & Interfaces"]
        Lifecycle["Component Lifecycle (Init, Start, Stop)"]
    end

    AppController --> L3
    L3 --> L2
    L2 --> L1
```

---

## 2. Inversion of Control (IoC) & Microkernel Rules

### The Golden Dependency Rule
> **Dependencies only point downwards.**
> A lower layer never imports or references a higher layer.

1. **Kernel / Core (Layer 1)**:
   - Does NOT know about AI providers, RAG, GUI windows, or specific tools.
   - Responsible solely for DI registration, lifecycle state machines, and base contracts.
2. **Services & EventBus (Layer 2)**:
   - Subsystems register services and publish events asynchronously.
   - Cross-subsystem communication occurs via typed events (`EventBus.publish()`) rather than tight direct coupling.
3. **Domain Subsystems (Layer 3)**:
   - Pure domain logic. No GUI code or presentation elements.
4. **Presentation & Application (Layer 4)**:
   - Orchestrates presentation without implementing low-level business logic.
   - Receives events and dispatches asynchronous tasks to worker threads.

---

## 3. Dependency Injection (DI) Container

ScholarOS utilizes a lightweight, reflection-free Dependency Injection Container (`scholaros.container.container.Container`):
- Services register instances or factory bindings (`container.add_instance()`).
- Components resolve dependencies via contract types (`container.resolve(ServiceClass)`).
- Facilitates 100% test isolation with zero monkeypatching of global state.

Next Step: Explore the physical directory and package layout in the [Module Structure Guide](module_structure.md).
