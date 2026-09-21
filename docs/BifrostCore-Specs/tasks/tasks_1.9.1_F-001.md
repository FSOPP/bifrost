---
title: Tasks 1.9.1 F-001 — Core Engine
id: F-001
kind: tasks
feature: F-001
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Tasks 1.9.1 F-001 — Core Engine

> Ordered, dependency-aware implementation tasks — plan only, no code.

D: this is an as-built inventory (code already shipped), not a forward plan. One row per unit of shipped work already in core/bifrost.go, core/network/.

## Task list

| Task | Description | Depends on | Artifact | Done-when | Status |
| --- | --- | --- | --- | --- | --- |
| F-001-T1 | Request queuing (`ProviderQueue`, `ChannelMessage` pooling) | — | core/bifrost.go:62-171 | F-001-TC10..TC18 pass | wip — unverified, run go test ./core/... -run 'TestProviderQueue_|TestChannelMessageHandoffIsExclusive' |
| F-001-T2 | Retry loop with exponential backoff + jitter | F-001-T1 | core/bifrost.go:6192 (`executeRequestWithRetries`) | F-001-TC1..TC6 pass | wip — unverified, run go test ./core/... -run TestExecuteRequestWithRetries|TestCalculateBackoff |
| F-001-T3 | Key rotation by error class (401/403 vs 429 vs 5xx/529) | F-001-T2 | core/bifrost.go:6234-6242 | F-001-TC7..TC9 pass | wip — unverified, run go test ./core/... -run TestPerKeyFailureStatusCodes|TestTransientServerStatusCodes|Test.*529 |
| F-001-T4 | Fallback provider chain (`handleRequest` fallback loop) | F-001-T2 | core/bifrost.go:5346-5419 | integration-level; no dedicated unit TC found in this scope, see PRD OPEN | wip — implemented, no dedicated unit test name found in this scope; covered only at integration level |
| F-001-T5 | Encrypted-reasoning strip-and-retry fail-soft | F-001-T2 | core/bifrost.go:6249-6255 | `internal/llmtests` compaction/encrypted-content tests (out of this doc's Go-unit scope) | wip — unverified, run make test-core PROVIDER=anthropic TESTCASE=TestCompaction (live-API, not run in this pass) |
| F-001-T6 | Provider lifecycle (add/update/remove, in-flight re-routing) | F-001-T1 | core/bifrost.go:3746 (`RemoveProvider`), core/bifrost.go:3826 (`UpdateProvider`) | F-001-TC15, F-001-TC16 pass | wip — unverified, run go test ./core/... -run TestUpdateProvider|TestRemoveProvider |
| F-001-T7 | Plugin pipeline invocation order (pre/post, LIFO post-hooks) | F-001-T1 | core/bifrost.go:205-231, core/bifrost.go:8117-8548 (`PluginPipeline`) | no dedicated unit test found in this scope — OPEN | wip — implemented, no dedicated unit test found for plugin pipeline ordering in this scope |
| F-001-T8 | Network client setup (proxy, SSRF guard, streaming client split) | — | core/network/http.go, core/network/ssrf.go | core/network/*_test.go pass | wip — unverified, run go test ./core/network/... |

## Execution order

1. F-001-T1 (queuing/pooling foundation)
2. F-001-T2 (retry loop, depends on T1's message shape)
3. F-001-T3, F-001-T4, F-001-T5 in parallel (all extend the retry loop independently)
4. F-001-T6 (provider lifecycle, independent of T2-T5 but shares T1's queue type)
5. F-001-T7 (plugin pipeline, wraps T1-T6)
6. F-001-T8 (network layer — no dependency on the others, could run in parallel with T1)

## Definition of done

Per status-model.md: a row moves `todo → wip → done` only through `docs_flow.py task`, and `done` requires the cited test command to have actually run and passed in this environment, with the command and result recorded in the note.
