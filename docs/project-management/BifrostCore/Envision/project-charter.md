---
title: Project Charter — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Project Charter — BifrostCore

> Define product vision, business value, target users and explicit project boundaries.

## Vision statement

This document reverses `core/` — the Go library module `github.com/maximhq/bifrost/core` [D: core/go.mod:1] — not a product being planned. `core/` implements request routing, provider abstraction (30+ methods across 20+ LLM providers), and MCP tool-calling orchestration [D: core/schemas/provider.go:681, core/providers (543 files), core/mcp (54 files)]. It has zero HTTP entrypoints of its own [D: survey — "HTTP surface: none found"]; it is consumed by `transports/bifrost-http` and `cli/` [D: repowise architecture map — `module_transports_bifrost_http_handlers -> module_core_providers`].

OPEN: who is "the business" for this module specifically — the vision, problem and change a forward charter would state are not recorded anywhere in `core/`. They may live in the top-level `README.md` or in `docs/` (Mintlify), which are out of this reversed scope.

## Business value

OPEN: no value driver or metric is stated in code or comments for `core/` as a unit. The nearest artifact is the module's own `changelog.md` [D: survey "In-repo documents" — `changelog.md`], which records what shipped, not why it mattered.

## Target users

I: the direct consumer of `core/` is another Go module in this workspace, not an end user — basis: `core/` has no entrypoint (`main` package) anywhere [D: survey "Entrypoints: none found"], and `go.work` lists `transports` and `cli` as sibling modules that import it [D: go.work:1].
OPEN: the human personas behind those integrations (which teams operate `transports/bifrost-http`, why `cli/` needed the same engine) are not recoverable from `core/`.

## In scope / Out of scope

| In scope (this reversed hub) | Out of scope |
| --- | --- |
| `core/` only: `bifrost.go`/`inference.go`/`network/` (F-001), `schemas/` (F-002), `providers/` (F-003), `mcp/` (F-004) | `transports/`, `framework/`, `plugins/*`, `ui/`, `cli/` — separate Go modules [D: go.work:1], each its own reverse-docs pass |
| The Go type/interface contract as the "API" | Any HTTP/wire contract — `core/` exposes none; that is `transports/bifrost-http`'s job |
| What the code and its tests demonstrably do | Why it was built that way — not recorded in `core/` |

## Success metrics

OPEN: no SLO, latency target or throughput number is expressed inside `core/` itself. AGENTS.md (repo root, outside this module) states "~11µs overhead at 5,000 RPS" as a whole-gateway claim, not a `core/`-only measurement, so it is not cited here as `core/`'s own metric — OPEN: is that number measured against `core/` in isolation or the full HTTP stack.

## Constraints and assumptions

- D: the workspace pins Go 1.27.0 [D: go.work — see `core/go.mod:3` `go 1.27.0`].
- D: `core/` declares 71 dependencies in `go.mod` [D: survey "Stacks" table — `go.mod | go | github.com/maximhq/bifrost/core | — | 71 deps`].
- I: `core/` is designed to run without any provider credentials present — basis: every provider's test file reads its API key from an env var and is written to skip rather than fail when absent (pattern repeated per provider, e.g. `providers/openai/openai_test.go:15`) — this is an assumption about test design, not a runtime guarantee, and OPEN whether the same holds for non-test code paths.
- OPEN: budget, timeline and compliance constraints — not expressed in code.

## Top risks

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| OPEN: business/roadmap risk | OPEN | OPEN | OPEN — not recoverable from code |
| I: `core/bifrost.go` and `core/providers/bedrock/responses.go` are both flagged bug magnets (highest fix-commit counts in the repo per the repowise index) — basis: repowise `get_health`/CLAUDE.md hotspot list names `core/bifrost.go` (42 bug fixes) and `core/providers/bedrock/responses.go` (55 bug fixes) as of commit `d0ac342fe` | Regressions concentrate in the request-queue core and the Bedrock converter | High (recurring, per churn history) | I: none stated in code — OPEN: is there a stabilization plan for these two files |
