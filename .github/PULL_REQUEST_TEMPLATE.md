## Description

Please provide a summary of the change, including the problem being solved or feature introduced, and relevant motivation/context.

Fixes #(issue)

---

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature (non-breaking change adding functionality)
- [ ] 💥 Breaking change (fix or feature causing existing functionality not to work as expected)
- [ ] 📝 Documentation update
- [ ] ⚡ Performance optimization
- [ ] 🔒 Security hardening

---

## Verification Checklist

Please verify each item before requesting review:

- [ ] My code adheres to the project's coding standards and style guidelines.
- [ ] I have executed `ruff check scholaros tests scripts` with **0 errors**.
- [ ] I have executed `mypy scholaros scripts` with **0 type errors**.
- [ ] I have executed `pytest -p no:langsmith -q` and all existing & new tests pass.
- [ ] I have added automated unit/integration tests covering this change.
- [ ] I have updated the relevant documentation in `docs/` if modifying user-facing or public APIs.
- [ ] If changing dependencies, I have maintained backwards-compatible boundaries in `pyproject.toml`.

---

## Operating System & Hardware Tested

- [ ] Windows 11 / Windows 10
- [ ] Linux (Ubuntu / Debian / Fedora)
- [ ] macOS (Apple Silicon / Intel)
