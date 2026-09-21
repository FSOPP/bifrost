---
title: Product Backlog — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Product Backlog — BifrostCore

> Prioritized feature/story list. The one place feature IDs are minted.

## Backlog

The four rows are the confirmed feature clusters for this reversed hub, not a forward-looking backlog — user-facing value and priority are not recorded in code and are marked `OPEN`.

| Feature ID | Title | Scope (module) | Size (by surveyed file count) [D:] | Value | Priority | PRD link |
| --- | --- | --- | --- | --- | --- | --- |
| F-001 | Core Engine | `core/bifrost.go`, `core/inference.go`, `core/network/` — 19 code files [D: survey "Module layout" — `.` 19 files, `network` 8 files] | M | OPEN | OPEN | `PRDs/prd_1.9.1_F-001-core-engine.md` |
| F-002 | Provider Abstraction | `core/schemas/` — 130 code files [D: survey "Module layout" — `schemas` 130 files] | L | OPEN | OPEN | `PRDs/prd_1.9.1_F-002-provider-abstraction.md` |
| F-003 | Provider Implementations | `core/providers/` — 543 code files [D: survey "Module layout" — `providers` 543 files] | XL | OPEN | OPEN | `PRDs/prd_1.9.1_F-003-provider-implementations.md` |
| F-004 | MCP Integration | `core/mcp/` — 54 code files [D: survey "Module layout" — `mcp` 54 files] | M | OPEN | OPEN | `PRDs/prd_1.9.1_F-004-mcp-integration.md` |

Not clustered as a feature: `core/internal/` (117 files — `llmtests` + `mcptests`, test infrastructure, documented per-feature in each `tests/test_1.9.1_F-*.md` instead of as its own PRD) and `core/pool/` (generic object pool, cross-cutting, folded into F-001's architecture doc).

## Prioritization rationale

OPEN: value, risk and dependency-based ordering is a planning decision, not a code fact. The table above is ordered by module dependency direction only — I: F-002 (schemas/types) is the dependency root for F-001, F-003 and F-004 — basis: repowise's import-graph edges show `core/providers -> types` (5,740 references) and `core/internal -> types` (4,130 references) as the two heaviest edges in the repo [D: repowise get_overview architecture map edges].

## Deferred

Nothing found deferred-and-recorded in `core/`. OPEN: any explicitly parked idea would be organisational memory (a ticket, a Slack thread), not something a code survey can see.
