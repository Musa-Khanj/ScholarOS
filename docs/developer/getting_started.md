# Developer Getting Started Guide

Welcome to the ScholarOS development environment! This guide walks you through setting up a local development environment, installing editable dependencies, and configuring development tools.

---

## 1. Repository Setup

Clone the repository and navigate into the workspace:

```bash
git clone https://github.com/Musa-Khanj/ScholarOS.git
cd ScholarOS
```

---

## 2. Virtual Environment & Editable Install

Create a virtual environment with Python 3.12, 3.13, or 3.14+:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install all dependencies in editable mode
pip install -e ".[all]"
```

The `.[all]` target installs:
- Core runtime dependencies (`langchain`, `langchain-ollama`, etc.)
- Development tools (`pytest`, `ruff`, `mypy`)
- Packaging tools (`build`, `wheel`, `setuptools`)

---

## 3. Tooling Verification

Verify your development tools:

```bash
# 1. Run unit and integration tests
pytest

# 2. Run Ruff linter
ruff check scholaros tests scripts

# 3. Run Mypy static type checker
mypy scholaros scripts
```

All commands should exit cleanly with 0 errors.

---

## 4. Coding Standards

- **Python Version Target**: Python 3.12+ (tested up to 3.14).
- **Type Annotations**: All public classes, methods, and functions must have explicit type annotations. Codebase maintains 0 mypy static type errors across 380+ source files.
- **Imports**: Clean import architecture; avoid circular imports. Core microkernel must not import higher-level application or GUI code.
- **Linting**: Strict Ruff checks (`select = ["E", "F", "W"]`).

Next Step: Read the [Developer Architecture Guide](architecture.md) to understand the layered subsystem design.
