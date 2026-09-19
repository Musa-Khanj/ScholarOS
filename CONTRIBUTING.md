# Contributing to ScholarOS

Thank you for your interest in contributing to **ScholarOS**! We welcome contributions from researchers, software engineers, and community developers who want to improve the state of AI-assisted scientific research.

---

## 🏛️ Code of Conduct

All contributors and maintainers are expected to adhere to open, welcoming, diverse, and respectful collaboration standards. Be kind, constructive, and focused on helping the scientific community build better research tools.

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Python 3.12, 3.13, or 3.14**
- **Git**
- Optional: **Ollama** installed locally for live offline model testing

### 2. Fork and Clone
```bash
git clone https://github.com/Musa-Khanj/ScholarOS.git
cd ScholarOS
```

### 3. Create a Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install ScholarOS in editable mode with development dependencies:
pip install -e ".[all]"
```

---

## 📐 Quality Standards & Verification

Before submitting a Pull Request, all three quality gates must pass:

### 1. Code Formatting & Linting (Ruff)
```bash
ruff check scholaros tests scripts
```
Ensure 0 errors and 0 warnings.

### 2. Static Type Analysis (Mypy)
```bash
mypy scholaros scripts
```
ScholarOS adheres to strict type annotations across all subsystems. Ensure 0 issues found.

### 3. Pytest Regression Suite
```bash
pytest -p no:langsmith -q
```
All 1,375+ unit, integration, and workload tests must pass.

### 4. Run Local CI Pipeline
You can run the full automated verification with one command:
```bash
python scripts/ci_check.py
```

---

## 🌿 Branching & Commit Conventions

### Branch Naming
- Features: `feat/feature-name`
- Bug Fixes: `fix/issue-description`
- Documentation: `docs/topic-name`
- Performance/Refactoring: `perf/area` or `refactor/subsystem`

### Conventional Commits
We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:
- `feat: add hybrid reciprocal rank fusion scoring`
- `fix: resolve citation manager ID collisions`
- `docs: update knowledge library ingestion guide`
- `test: add end-to-end integration tests for research agent`
- `refactor: optimize in-memory vector store heap sort`

---

## 🚀 Pull Request Checklist

When submitting a Pull Request:
1. **Title**: Clear, descriptive summary following conventional commit conventions.
2. **Context**: Explain the motivation, problem solved, and architectural impact.
3. **Tests**: Include automated tests covering the new functionality or regression fix.
4. **Documentation**: Update relevant user or developer documentation in `docs/` if modifying user-facing or public APIs.
5. **CI Passing**: Ensure GitHub Actions checks pass cleanly across all platforms (Ubuntu, Windows, macOS).

Thank you for helping push scientific research AI forward!
