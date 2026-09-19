# Security Policy

## Supported Versions

ScholarOS actively maintains and releases security patches for the following versions:

| Version | Supported          | Security Maintenance Status |
| ------- | ------------------ | --------------------------- |
| 1.0.x   | :white_check_mark: | Active support (current)    |
| < 1.0.0 | :x:                | End of life / unsupported   |

---

## Reporting a Vulnerability

The ScholarOS core engineering team takes the security of scientific research data, local model inference, and extensible plugins seriously. If you discover a security vulnerability in ScholarOS, please do **NOT** report it in a public GitHub issue.

### How to Report Privately
Please disclose the vulnerability via one of the following confidential channels:
1. **GitHub Private Vulnerability Reporting**: Submit a private advisory via [GitHub Security Advisories](https://github.com/Musa-Khanj/ScholarOS/security/advisories/new).
2. **Direct Security Email**: Send details to `security@scholaros.org` (or directly contact project maintainers).

### What to Include
To help us triage and resolve the issue quickly, please include:
- A clear description of the vulnerability and its potential impact.
- Step-by-step reproduction instructions or a minimal Proof of Concept (PoC).
- Affected version(s) and operating systems (Windows, Linux, macOS).
- Any proposed remediation or mitigation steps.

---

## Response & Disclosure SLA

1. **Initial Acknowledgement**: Within **48 hours** of receiving your report, a maintainer will confirm receipt and begin validation.
2. **Triage & Assessment**: Within **5 business days**, we will provide an initial assessment of the issue and discuss next steps.
3. **Patch & Release**: For confirmed high- or critical-severity issues, patches will be engineered, verified against our regression suite, and released in a patch update (e.g. `1.0.1`) within **14 days**.
4. **Public Disclosure**: Coordinated disclosure will occur after the fix is publicly released and users have had sufficient time to update.

---

## Security Architecture & Threat Model

ScholarOS is engineered with built-in defenses:
- **Local-First Isolation**: Zero telemetry or research queries leave the local system when using offline providers (`ollama`, `mock`).
- **Prompt Injection Hardening**: Context boundary framing, XML tag escaping, and injection heuristic auditing (`scholaros.security.sanitizer`).
- **Path Traversal Defenses**: All file reads/writes in the knowledge library and plugin runtime are strictly sandboxed against workspace roots.
- **Plugin Sandbox & Capabilities**: Plugins run in an isolated execution harness restricted by declared capability permissions (`PluginManifest`).
- **Credential Redaction**: Automatic masking of sensitive tokens (`sk-...`, `Bearer ...`) in application logs and telemetry streams.
