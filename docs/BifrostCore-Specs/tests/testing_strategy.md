---
title: Testing Strategy — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Testing Strategy — BifrostCore

> Test levels, tooling, coverage rules and pipeline gates.

## Test levels

D: `core/` has 454 test files totalling 4,385 test cases [D: survey "Tests" — "files: 454, cases: 4385"], entrypoint `go test ./...` [D: core/go.mod:1].

| Level | Scope | Tool | Who owns | When it runs |
| --- | --- | --- | --- | --- |
| Unit | Converter functions, schema validation, retry/rotation logic | `go test` (standard library) | Per-package `*_test.go` | Local + CI (I: CI wiring not independently re-verified in `core/`'s own config — none found scoped to `core/`; repo-wide `.github/workflows/` exists per repowise's tree but wasn't cited line-by-line here) |
| Provider scenario ("llmtests") | End-to-end behaviour against **live provider APIs**, dual Chat-Completions + Responses API | `make test-core` [I: basis — AGENTS.md's stated command, not `core/`-internal] | `core/internal/llmtests/` (65 files per repowise module count) | Opt-in, requires provider API keys (survey lists 40+ secret-shaped env vars, e.g. `OPENAI_API_KEY` at `providers/openai/openai_test.go:15`) |
| MCP/agent (mock-based) | Agent loop, tool/client lifecycle, no live APIs | `make test-mcp` [I: same basis] | `core/internal/mcptests/` | Local + CI, no credentials needed |
| Provider harness | Wire-level, HTTP-visible behaviour | `make run-provider-harness-test` | `tests/e2e/api/collections/` — **outside `core/`**, since `core/` has no HTTP surface (survey: 0 endpoints) | Not applicable to `core/` in isolation |

## Coverage policy

OPEN: no numeric coverage threshold was found scoped to `core/`. I: the domain doc's 10 promoted rules (DOM-001-R1..R10) are the closest thing to a required-coverage list, each pointing at a named test or comment [D: domain doc's Implementation status table] — 2 of the 10 (R7, R8) have no test name found in the cited evidence, which is a coverage gap, not a false claim.

## Test data

D: fixtures live under `data/fixtures/fixtures_1.9.1_F-*.json`, documented per feature in `data/data-fixtures_1.9.1_F-*.md` (owned by each feature's own reversal pass). OPEN: anonymisation policy for any recorded provider response fixture — not stated in code.

## Pipeline gates

OPEN: no CI configuration was found scoped to `core/` (survey "Ops" — "ci: none"). I: AGENTS.md states a repo-wide rule that every fix ships with a regression test and every wire-visible change ships with a provider-harness case — since `core/` has no wire surface, the harness half of that rule is structurally inapplicable to `core/` alone; the regression-test half is not independently re-verified against `core/`'s actual merge history in this pass.

## Non-functional testing

OPEN: no performance, security or accessibility test with a stated threshold was found scoped to `core/`.

## Why the live-API suite was not run in this pass

Per `filling.md`'s "Status from evidence" rule: run the test command through the project's own manifest and **ask before running it**. `make test-core`/`go test ./...` in `core/` includes `internal/llmtests`, which calls live provider APIs and costs money per AGENTS.md ("Core tests — provider integration tests — hit live APIs"), and no `.env`/API keys are present in this environment. This reversal did not run the suite; every status cell in this hub that depends on a test result is `wip — unverified, run <command>`, which `filling.md` calls "a completely acceptable outcome and the honest one."
