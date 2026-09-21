---
title: How to Test — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# How to Test — BifrostCore

> How to run and extend tests locally and in CI.

## Running tests

I: from AGENTS.md (repo root, not `core/`-internal), not run in this pass:
- `go test ./...` inside `core/` — unit level, no live calls if no provider env vars are set.
- `make test-core PROVIDER=<name>` — live-API scenario tests, costs money, requires that provider's key.
- `make test-mcp` — mock-based agent/tool tests, no live calls.

## Adding a test

D: per AGENTS.md's stated repo convention — add to the existing `<name>_test.go` next to `<name>.go`, never a new test file for a package that already has one. Filenames never contain an underscore except the `_test.go` suffix (see `architect_common.md` Naming conventions).

## Interpreting failures

| Failure type | First thing to check |
| --- | --- |
| Live-API test fails | Is the required provider env var set and valid (survey "Configuration keys" lists the name per provider, never the value) |
| Unit test fails after a `schemas/` change | Every provider's converter (`providers/*/chat.go` etc.) that consumes the changed type — AGENTS.md gotcha #6/#5 |
| OPEN: other failure classes | not enumerated in this pass |

## Pointer

Strategy, coverage policy and the rationale for not running the live suite in this reversal live in `tests/testing_strategy.md` — not restated here.
