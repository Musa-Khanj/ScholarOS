# ADR-0001: Kernel-First Architecture

## Status

Accepted

## Context

ScholarOS is intended to become a long-lived, extensible AI research platform supporting multiple orchestration frameworks, models, tools, and research domains.

## Decision

The Kernel is the central runtime authority. All framework services, plugins, agents, and tools are initialized through the Kernel. No component may bypass it.

## Consequences

- Consistent lifecycle management.
- Framework independence.
- Improved testability.
- Easier plugin integration.
- Cleaner dependency management.