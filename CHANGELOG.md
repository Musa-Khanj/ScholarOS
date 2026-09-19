# Changelog

All notable changes to ScholarOS are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-09-19

### Added
- **Core Microkernel**: Microkernel architecture, lifecycle state machine (`INITIALIZED`, `RUNNING`, `STOPPED`), abstract component contracts.
- **Dependency Injection**: Lightweight, reflection-free DI `Container` with instance and factory binding registration.
- **AI Subsystem**: High-level `AIClient`, `AIManager`, `PromptCatalog`, and providers for Ollama (local offline), OpenAI, Anthropic Claude, Google Gemini, OpenRouter, and Mock testing.
- **Knowledge Library**: Multi-format document ingestion engine with `PDFAdapter`, `MarkdownAdapter`, `TextAdapter`, and `JSONAdapter`, featuring sliding-window text chunking.
- **Vector Embeddings**: Normalized vector representation with cached norms, `InMemoryVectorStore` with RLock thread safety, and $O(N \log k)$ heap-based top-$k$ nearest neighbor search.
- **Hybrid Retrieval**: `HybridRetriever` fusing BM25 keyword matching and dense vector search via Reciprocal Rank Fusion (RRF); thread-safe LRU/TTL `RetrievalCache` with sub-millisecond (<0.5ms) latency.
- **Retrieval-Augmented Generation (RAG)**: Multi-stage `RAGPipeline`, grounded context assembly, relevance threshold filtering, and structured `RAGResponse`.
- **Research Engine**: Autonomous research planner, task decomposition (`ResearchTask`), session management (`ResearchSession`), citation graphs (`CitationManager`), and report generation (`ResearchReport`).
- **Memory Subsystem**: Short-term conversational memory and long-term research associative memory collections.
- **Tools & Plugins**: Sandboxed, capability-gated plugin architecture (`PluginManifest`, `PermissionSet`, `PluginSandbox`), computational tool abstractions, and built-in `SystemMetricsPlugin`.
- **Desktop GUI Application**: Production Tkinter desktop interface with navigation views (Chat, Research, Library, Plugins, Settings) and non-blocking background `ThreadPoolExecutor` workers.
- **Platform Directory Standards**: OS-conforming directory resolution for Windows (`%APPDATA%`, `%LOCALAPPDATA%`), Linux (XDG Base Directory specification), and macOS.
- **Windows Packaging**: PyInstaller standalone specification (`packaging/windows/scholaros.spec`) and zero-console launcher (`scholaros-desktop`).
- **Documentation Suite**: Comprehensive user guides, developer guides, and architecture references covering all 17 subsystems.
- **CI/CD & Release Engineering**: Multi-platform GitHub Actions workflows (CI, Release, Nightly), local CI runner (`scripts/ci_check.py`), and release orchestrator (`scripts/release.py`).
- **Public API & Architecture Freeze**: Top-level public interface surface frozen in `scholaros.__all__` and reproducible production dependency lockfile generated in `requirements-frozen.txt`.
- **Open-Source Governance & Legal**: Official Apache License 2.0 (`LICENSE`), comprehensive security policy and responsible disclosure SLA (`SECURITY.md`), contributor guidelines (`CONTRIBUTING.md`), GitHub Issue Forms, and PR template.
- **Release Notes & Candidate Sign-Off**: Official General Availability release announcement and quality verification sign-off (`RELEASE_NOTES.md`).

---

## [0.1.0] - 2026-09-01

### Added
- Initialized ScholarOS repository and architectural vision.