# ScholarOS V1.0.0 Release Notes

**Release Date**: September 19, 2026  
**Status**: General Availability (Production / Stable)  
**Distribution**: Wheel, Source Archive, Windows Standalone Specs  

---

## 🌟 Welcome to ScholarOS V1.0.0

The ScholarOS team is proud to announce the official **V1.0.0 General Availability** release of **ScholarOS** — a modular, multi-agent AI research operating system designed to give scientists, engineers, and researchers complete ownership, privacy, and precision over their literature discovery, synthesis, and experiment workflows.

With V1.0.0, the ScholarOS architecture, core dependencies, and public APIs are officially **frozen and stabilized** under Semantic Versioning 2.0.

---

## 🏛️ Architecture & API Freeze

The V1.0.0 release establishes strict backward-compatibility guarantees:
1. **Microkernel Core**: Pure Python, zero-reflection Dependency Injection Container (`scholaros.Container`), EventBus (`scholaros.EventBus`), and formal component lifecycles (`INITIALIZED`, `RUNNING`, `STOPPED`).
2. **Frozen Public API**: The top-level `scholaros` module exports the core public API surface:
   ```python
   import scholaros

   print(scholaros.__all__)
   # ['AIFactory', 'Container', 'EventBus', 'GUIApplication', 'HybridRetriever',
   #  'Kernel', 'KnowledgeManager', 'Plugin', 'RAGPipeline', 'ResearchAgent', '__version__']
   ```
3. **Frozen Lockfile**: Reproducible production environment locked in `requirements-frozen.txt`.

---

## 🚀 Key Feature Highlights

### 🔒 1. Local-First & Privacy-Preserving
- Direct offline inference with **Ollama** (`qwen2.5:1.5b`, `llama3.2:3b`, `deepseek-r1:1.5b`).
- Zero telemetry or private research data is transmitted over the network when running local models.
- Modular cloud provider fallbacks for OpenAI, Anthropic Claude, Google Gemini, and OpenRouter when configured by the user.

### ⚡ 2. Hybrid Reciprocal Rank Fusion & Sub-Millisecond Caching
- Seamlessly fuses sparse lexical matching (BM25) with dense semantic embeddings (cosine similarity) using Reciprocal Rank Fusion (RRF).
- Backed by an optimized $O(N \log k)$ heap vector store capable of querying 5,000 dense vectors in under 150ms.
- Built-in thread-safe LRU/TTL `RetrievalCache` serving repeated literature queries in **< 0.1ms**.

### 📚 3. Universal Knowledge Library & Multimodal Ingestion
- Ingests academic literature from PDF, Markdown, Plain Text, and JSON documents.
- Configurable sliding-window chunking with boundary preservation.
- Automatic metadata tagging for DOI, author, title, and citation tracking.

### 🔬 4. Autonomous Multi-Stage Research Agent
- Iterative query decomposition into structured `ResearchTask`s.
- Synthesizes findings across multiple papers with explicit provenance attribution.
- Full academic citation graph tracking via `CitationManager` with exportable Markdown research reports.

### 🖥️ 5. Native Desktop GUI & CLI
- **Desktop Application (`scholaros-desktop`)**: Full-featured Tkinter desktop interface with views for AI Chat, Research Projects, Knowledge Library, Plugins, and Settings.
- **Non-Blocking Architecture**: Long-running model inference, retrieval, and document ingestion run asynchronously on dedicated background worker threads to keep the UI interactive.
- **Unified CLI (`scholaros`)**: Single binary command providing `init`, `config`, `run`, `status`, `info`, and `gui`.

### 🛡️ 6. Enterprise Security & Hardening
- Built-in prompt injection defense with context framing and XML tag escaping.
- Strict path traversal defenses preventing directory breakouts during document ingestion or plugin execution.
- Capability-gated plugin sandbox restricting tool permissions.
- Automatic redaction of sensitive credentials (`sk-...`, `Bearer ...`) from application logs.

---

## 📊 Verification & Quality Benchmarks

ScholarOS V1.0.0 has passed the most rigorous verification cycle in the project's history:

| Metric | Result |
|---|---|
| **Test Suite Passage** | **1,377 passed, 2 skipped (100% pass rate)** |
| **Static Type Analysis** | **0 errors across 388 source files** (`mypy`) |
| **Code Style & Linting** | **0 warnings / 0 errors** (`ruff`) |
| **Documentation Integrity** | **20 doc files, 0 broken links** |
| **Retrieval Cache Latency** | **< 0.1ms** |
| **Vector Store Scale (5,000 items)** | **< 150ms** |
| **Clean Machine Wheel Extraction** | **Verified** |

---

## 📦 Installation & Quickstart

### Standard Pip Installation
```bash
# In a Python 3.12+ virtual environment:
pip install scholaros

# Initialize your environment:
scholaros init

# Launch the desktop GUI:
scholaros gui
# Or use the zero-console Windows launcher:
scholaros-desktop
```

### Reproducible Locked Installation
```bash
pip install -r requirements-frozen.txt
pip install --no-deps dist/scholaros-1.0.0-py3-none-any.whl
```

---

## 🔐 Cryptographic Checksums (dist/SHA256SUMS.txt)

```text
adc879f13f5cb3d8ae0168fad94f830ed2915214ab16e5eecb311e0ad70dc3a0  scholaros-1.0.0-py3-none-any.whl
e5f7174347bc1dcdaa579032e326a7a73caf6175acd8bf294b4b8975231f2d37  scholaros-1.0.0.tar.gz
```

---

## 📄 License & Governance

ScholarOS is proudly released under the open-source **Apache License 2.0**.  
See [LICENSE](LICENSE), [SECURITY.md](SECURITY.md), and [CONTRIBUTING.md](CONTRIBUTING.md) for community details.
