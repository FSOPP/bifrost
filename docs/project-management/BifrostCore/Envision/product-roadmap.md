---
title: Product Roadmap — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Product Roadmap — BifrostCore

> High-level, outcome-oriented roadmap. Themes and horizons, not dated Gantt charts.

## Now / Next / Later

This is a reversed hub, not a forward plan — there is no roadmap encoded in `core/`'s code. What follows is an as-built ordering, not a plan: the git history's most-changed files [D: survey "History" — `core/bifrost.go`(26), `framework/configstore/rdb.go`(24) among repo-wide top churn, and repowise's hotspot list: `core/providers/bedrock/responses.go` (55 bug fixes), `core/providers/anthropic/responses.go` (46 bug fixes)] show where change has concentrated recently.

| Theme | Recent evidence | Confidence |
| --- | --- | --- |
| I: provider response-shape stabilization (Bedrock, Anthropic) — basis: both files are the two highest bug-fix-count files in the whole repo per the repowise health index | `core/providers/bedrock/responses.go`, `core/providers/anthropic/responses.go` | med (churn-derived, not a stated plan) |
| I: core request-queue/retry hardening — basis: `core/bifrost.go` is the 4th-highest bug-fix file repo-wide and the single most-changed file in `core/` by commit count | `core/bifrost.go` | med |
| OPEN: actual forward roadmap, themes, target dates | — | — |

## Release themes

OPEN: `core/`'s own `changelog.md` records what shipped per version but not a thematic grouping tied to success metrics (which are themselves OPEN in the charter).

## Dependencies

- D: `core/` is a workspace module; `transports`, `cli` and the plugin modules import it and must stay in lockstep on its `Provider` interface (30+ methods) [D: core/schemas/provider.go:681] — a breaking change there is a cross-module dependency, per AGENTS.md's "Provider Interface Has 30+ Methods" gotcha (repo root, not `core/` itself, so not cited as `[D:]` here).
- OPEN: any external system or team dependency gating a `core/`-only release.
