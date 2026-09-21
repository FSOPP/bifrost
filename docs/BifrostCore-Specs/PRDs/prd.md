---
title: Master PRD — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Master PRD — BifrostCore

> Product scope, MVP definition and the index of all child PRDs.

## Problem and outcome

OPEN: intent is not in the repository (per `filling.md`'s own rule: "A PRD holds no paths, no schemas, no file references" and no rationale). I: what the shipped code demonstrably solves — basis: `core/` provides one Go interface (`Provider`, 30+ methods [D: core/schemas/provider.go:681]) behind which 20+ LLM/voice/image backends are interchangeable [D: survey "Module layout" — `providers` 543 files], so the observable outcome is "swap or add a provider without changing caller code." Whether that was *the* problem being solved, or a side effect of another goal, is OPEN.

## MVP definition

OPEN: no MVP boundary is recorded. The current shipped surface (all four features, version `1.9.1` [D: core/version:1]) is already far past any inferable MVP slice.

## Personas and top user flows

OPEN: see `project-charter.md`'s Target users section — the direct consumer is another Go module (`transports/`, `cli/`), not a named human persona.

## Child PRD index

| Version | Feature ID | Title | Status | Link |
| --- | --- | --- | --- | --- |
| 1.9.1 | F-001 | Core Engine | draft | `PRDs/prd_1.9.1_F-001-core-engine.md` |
| 1.9.1 | F-002 | Provider Abstraction | draft | `PRDs/prd_1.9.1_F-002-provider-abstraction.md` |
| 1.9.1 | F-003 | Provider Implementations | draft | `PRDs/prd_1.9.1_F-003-provider-implementations.md` |
| 1.9.1 | F-004 | MCP Integration | draft | `PRDs/prd_1.9.1_F-004-mcp-integration.md` |

## Non-functional requirements

Per `filling.md`: cite only where a number is literally configured, otherwise `OPEN`.
- OPEN: latency/throughput target for `core/` in isolation (AGENTS.md's "~11µs at 5,000 RPS" is a whole-gateway claim including `transports/`, not re-derived from a `core/`-only benchmark in this pass).
- OPEN: availability target.
- D: default connection pooling is configurable per provider via `NetworkConfig.MaxConnsPerHost` (AGENTS.md states a default of 5000, 30s idle — not independently re-verified against a `core/schemas/provider.go` line citation in this pass, so treated as `I:` here, not `D:`).
- OPEN: accessibility/compliance — not applicable to a backend library, or not recorded if it is.

## Traceability

| Feature ID | Domain doc | Architecture | Tasks | Tests |
| --- | --- | --- | --- | --- |
| F-001 | `ddd/domain_DOM-001-core-engine.md` (shared) | `architect/feature_1.9.1_F-001_architect.md` | `tasks/tasks_1.9.1_F-001.md` | `tests/test_1.9.1_F-001.md` |
| F-002 | `ddd/domain_DOM-001-core-engine.md` (shared) | `architect/feature_1.9.1_F-002_architect.md` | `tasks/tasks_1.9.1_F-002.md` | `tests/test_1.9.1_F-002.md` |
| F-003 | `ddd/domain_DOM-001-core-engine.md` (shared) | `architect/feature_1.9.1_F-003_architect.md` | `tasks/tasks_1.9.1_F-003.md` | `tests/test_1.9.1_F-003.md` |
| F-004 | `ddd/domain_DOM-001-core-engine.md` (shared) | `architect/feature_1.9.1_F-004_architect.md` | `tasks/tasks_1.9.1_F-004.md` | `tests/test_1.9.1_F-004.md` |

Only one domain document exists in this hub (`DOM-001`) — it is shared across all four features rather than split per feature, since `core/`'s stated constraints did not cluster cleanly by feature boundary. See the domain doc's own scope note.
