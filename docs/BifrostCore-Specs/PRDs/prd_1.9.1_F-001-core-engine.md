---
title: PRD 1.9.1 F-001 — Core Engine
id: F-001
kind: prd
feature: F-001
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# PRD 1.9.1 F-001 — Core Engine

> Feature-level requirements: what and why, never how.

## Summary

I: Core Engine gives every caller of the Bifrost Go library a single request path — queue, retry, key rotation, fallback, plugin hooks — regardless of which of the ~60 request types or which of the 20+ providers is targeted, so provider-specific reliability logic is written once instead of per-integration. Business value, priority and target users beyond "a caller of the Bifrost library" are OPEN — not stated anywhere in core/.

## User stories

- F-001-US1: As a caller of Bifrost, I want a failed request automatically retried with backoff so that transient provider errors don't surface to my application. [tests: F-001-TC1..TC6]
- F-001-US2: As a caller of Bifrost, I want a request to rotate to a different API key when the current one is rate-limited or rejected, without burning other keys on errors that aren't the key's fault, so that I get the highest chance of success from my configured key pool. [tests: F-001-TC7..TC9]
- F-001-US3: As an operator, I want a provider to be removed or hot-updated without dropping in-flight requests or panicking on a closed channel, so that config changes don't cause an outage. [tests: F-001-TC10..TC16]
- F-001-US4: As a caller, I want my request's terminal result billed and logged exactly once even if I cancel at the same instant a worker finishes it, so that usage accounting is never double-counted or lost. [tests: F-001-TC17]

## Acceptance criteria

- F-001-US1: Given a provider returns a 5xx, when the retry budget (`config.NetworkConfig.MaxRetries`) is not exhausted, then the same key is retried after a computed backoff [D: core/bifrost.go:6234-6242, tests at core/bifrost_test.go:56,131,236].
- F-001-US2: Given a provider returns 401/403, when a retry is attempted, then a different key is selected and backoff is suppressed; given a 429, then a different key is selected and backoff is NOT suppressed [D: core/bifrost.go:6234-6242, test at core/bifrost_test.go:796].
- F-001-US3: Given `RemoveProvider` is called while requests are queued, when the queue drains, then every buffered message receives an error response rather than being silently dropped [D: core/bifrost.go:8870, test at core/bifrost_test.go:2837].
- F-001-US4: Given a caller's context is cancelled at the same instant a worker completes the request, when both sides race on `handoff`, then exactly one of them (never both, never neither) delivers/bills the result [D: core/bifrost.go:88-97, test at core/abandonedstream_test.go:443].

## Implementation status

| Story | Status | Evidence |
| --- | --- | --- |
| F-001-US1 | wip | unverified — run `go test ./core/... -run TestExecuteRequestWithRetries`; covers F-001-TC1..TC6, F-001-T2 |
| F-001-US2 | wip | unverified — run `go test ./core/... -run TestPerKeyFailureStatusCodes`; covers F-001-TC7..TC9, F-001-T3 |
| F-001-US3 | wip | unverified — run `go test ./core/... -run TestRemoveProvider`; covers F-001-TC10..TC16, F-001-T1/T6 |
| F-001-US4 | wip | unverified — run `go test ./core/... -run TestChannelMessageHandoffIsExclusive`; covers F-001-TC17, F-001-T1 |

## Scope boundaries

- Out of scope: provider-specific request/response conversion (F-003), MCP tool orchestration (F-004), the public HTTP surface (`transports/bifrost-http/`, a separate module entirely, not surveyed in this pass).
- Out of scope: the `schemas.Provider` interface contract itself and `BifrostContext` (F-002 Provider Abstraction).

## Dependencies

- F-002 (Provider Abstraction) — Core Engine calls the `schemas.Provider` interface and reads/writes `schemas.BifrostContext`; it does not define either.
- F-004 (MCP Integration) — `tryRequest` calls `bifrost.MCPManager.AddToolsToRequest` when MCP is configured [D: core/bifrost.go:5588-5591].

## Metrics

OPEN: no success metric (latency target, error-rate target, retry-success rate) is expressed anywhere in core/. `NetworkConfig.MaxRetries`, backoff parameters, and queue size are operator-configured, not fixed targets the design was validated against.
