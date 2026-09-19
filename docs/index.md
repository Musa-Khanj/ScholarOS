# ScholarOS Documentation Portal

Welcome to the **ScholarOS** documentation. ScholarOS is a modular, multi-agent AI research operating system designed for scientific literature review, retrieval-augmented generation (RAG), experiment management, and local-first research assistance.

---

## 📚 Documentation Map

```
docs/
├── user/                  # End-User & Research Guides
│   ├── installation.md    # Installation & System Requirements
│   ├── first_launch.md    # Initial Bootstrapping & CLI Commands
│   ├── llm_configuration.md# Local (Ollama) & Cloud Model Setup
│   ├── ai_chat.md         # Interactive AI Chat & Multi-turn Sessions
│   ├── research_workflow.md# End-to-end Academic Research & Synthesis
│   ├── knowledge_library.md# Document Ingestion (PDF, TXT, MD, JSON)
│   ├── rag_configuration.md# RAG Strategies, Caching & Reranking
│   ├── plugins.md         # Managing Plugins & Capability Permissions
│   └── troubleshooting.md # Diagnostic Steps & Common Solutions
│
├── developer/             # Developer & Contributor Guides
│   ├── getting_started.md # Dev Environment Setup & Editable Install
│   ├── architecture.md    # Layered System Design & Inversion of Control
│   ├── module_structure.md# Deep Dive into all 30+ ScholarOS Packages
│   ├── extension_points.md# Hooks, Extensions & Lifecycle Interceptors
│   ├── plugin_development.md# Authoring Plugins, Manifests & Sandboxes
│   ├── provider_development.md# Creating Custom AI & Embedding Providers
│   ├── testing.md         # Testing Disciplines, Workloads & Static Analysis
│   └── contributing.md    # Contribution Process, Style & PR Guidelines
│
└── architecture/          # Exhaustive Technical Specifications
    ├── reference.md       # Comprehensive 17-Subsystem Architecture Reference
    └── diagrams.md        # Mermaid Flowcharts, Sequence & Runtime Topology
```

---

## 🚀 Quick Navigation

| What are you trying to do? | Recommended Guide |
|---|---|
| **Install ScholarOS on Windows, Linux, or macOS** | [User Installation Guide](user/installation.md) |
| **Configure Local Models (Ollama) or Cloud APIs (OpenAI/Anthropic)** | [LLM Configuration Guide](user/llm_configuration.md) |
| **Import Research Papers & PDFs into the Knowledge Base** | [Knowledge Library Guide](user/knowledge_library.md) |
| **Run Academic Literature Searches from the CLI or Desktop GUI** | [Research Workflow Guide](user/research_workflow.md) |
| **Tune RAG Retrieval Scores, Filters, and Caching** | [RAG Configuration Guide](user/rag_configuration.md) |
| **Fix Launch, Path, or Model Connection Errors** | [Troubleshooting Guide](user/troubleshooting.md) |
| **Set Up a Local Development Environment** | [Developer Getting Started](developer/getting_started.md) |
| **Build a Custom Plugin or Tool** | [Plugin Development Guide](developer/plugin_development.md) |
| **Integrate a New LLM or Vector Provider** | [Provider Development Guide](developer/provider_development.md) |
| **Understand the Internal Architecture and Subsystems** | [Architecture Reference](architecture/reference.md) |
