---
title: Runbook (DEV) — Local Setup
id: RB-001
kind: runbook
feature: F-001
status: draft
owner: TBD
updated: 2026-09-21
---

# Runbook (DEV) — Local Setup

> Get a working local environment from a clean checkout.

## Preconditions

- D: Go 1.27.0, pinned by the workspace [D: core/go.mod:3 `go 1.27.0`].
- I: no provider API key is required to build or run the non-live-API test suite — basis: per-provider test files gate on env vars and are written to skip rather than fail when absent (pattern repeated per provider, e.g. `providers/anthropic/anthropic_test.go:15`); not independently re-run in this pass to confirm the skip actually fires.

## Steps

I: every command below is taken from AGENTS.md's stated Build/Test/Dev commands (repo root, not `core/`-internal) — marked `I:` because none were executed in this session:
1. `git clone` / `cd` into the repo (assumed).
2. I: `make dev` — full local dev (UI + API with hot reload via `air`).
3. I: `make build` — build the `bifrost-http` binary.
4. I: `make test-core PROVIDER=<name>` — run one provider's scenario tests (**hits live APIs**, requires that provider's key).

## Verification

I: `go build ./...` inside `core/` succeeding, and `go test ./...` in `core/` with no provider env vars set (expected: live-API-gated tests skip rather than fail) — neither was run in this pass; this is the check someone else can run, not a result observed here.

## Rollback / cleanup

OPEN: no rollback/cleanup procedure is stated in code for a local `core/` checkout beyond standard `git clean`/`go clean` — not `core/`-specific.

## Common failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| I: provider test fails instead of skipping | Missing/malformed API key env var while attempting a live call — basis: the per-provider skip pattern (see Preconditions) implies a present-but-invalid key could reach the live call and fail rather than skip; not independently reproduced in this pass | Unset the var, or supply a valid key |
| `go build` fails on workspace resolution | Go version below 1.27.0 [D: core/go.mod:3] | Upgrade Go toolchain |
| OPEN: other failure modes | — | — |
