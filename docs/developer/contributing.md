# Contributing to ScholarOS

Thank you for your interest in contributing to ScholarOS! We welcome contributions from researchers, software engineers, security professionals, and documentation writers.

---

## 1. Development Workflow

1. **Fork & Clone**: Fork the repository and clone your fork locally.
2. **Branch**: Create a descriptive feature branch:
   ```bash
   git checkout -b feature/hybrid-rrf-optimization
   ```
3. **Set Up Environment**: Install editable packages and dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
   pip install -e ".[all]"
   ```
4. **Make Changes**: Implement your changes adhering to existing design patterns.
5. **Add Tests**: Write comprehensive tests in `tests/` covering your changes.
6. **Verify Quality**:
   ```bash
   ruff check scholaros tests scripts
   mypy scholaros scripts
   pytest -q
   ```
7. **Commit**: Use concise, conventional commit messages:
   - `feat(retrieval): add reciprocal rank fusion weight tuning`
   - `fix(gui): prevent main thread freeze on large document imports`
   - `docs(user): expand ollama model setup guide`
8. **Submit PR**: Open a Pull Request against `main`.

---

## 2. Coding Conventions

- **Clean Layering**: Maintain strict separation between UI, domain logic, and core services. Never import UI or CLI modules inside domain or kernel code.
- **Async GUI Safety**: Any operation taking longer than 50 milliseconds must be dispatched via background thread workers (`execute_async`) in the GUI application.
- **Defensive Error Handling**: Catch and wrap subsystem errors in domain-specific exceptions inheriting from `ScholarOSError`.
- **Security First**: Sanitize all document paths, validate external plugin manifests, and isolate untrusted RAG contexts.

---

## 3. Pull Request Review Process

Every PR undergoes automated and peer review checks:
- **Continuous Integration**: Test suite must pass 100% across all supported Python versions.
- **Zero Type Regressions**: Mypy must report 0 errors.
- **Documentation**: Any public API changes or new features must be documented in `docs/`.

Next Step: Deep-dive into internal subsystem architecture in the [Architecture Reference](../architecture/reference.md).
