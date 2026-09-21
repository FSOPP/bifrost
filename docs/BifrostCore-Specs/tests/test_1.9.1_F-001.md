---
title: Test Plan 1.9.1 F-001 — Core Engine
id: F-001
kind: test
feature: F-001
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Test Plan 1.9.1 F-001 — Core Engine

> Concrete cases traced back to acceptance criteria.

D: this document inverts its usual meaning — it records what was built and tested, not what is planned. Scope's Go test suite (core/bifrost_test.go, core/abandonedstream_test.go, core/azurestreamretry_test.go, core/encryptedreasoning_test.go, core/streamfallback_test.go, core/promptcache*_test.go, core/spanenrichment_test.go, core/utils*_test.go, core/overhead_e2e_test.go, core/modelcataloghooks_test.go, core/gpt6astrae2e_test.go, core/network/*_test.go) contains 153 `func Test*` top-level functions [D: `grep -c "^func Test"` over the listed files, run in this session].

## Traceability matrix

| Story (see PRD) | Test cases | Level |
| --- | --- | --- |
| F-001-US1 (retry & backoff) | F-001-TC1..TC6 | unit |
| F-001-US2 (key rotation by error class) | F-001-TC7..TC9 | unit |
| F-001-US3 (provider queue lifecycle) | F-001-TC10..TC16 | unit (some race-focused, run with `-race`) |
| F-001-US4 (channel-message handoff exclusivity) | F-001-TC17..TC18 | unit |

## Test cases

| ID | Test function | Cited at | What it proves |
| --- | --- | --- | --- |
| F-001-TC1 | `TestExecuteRequestWithRetries_SuccessScenarios` | core/bifrost_test.go:56 | happy-path retry loop returns on first success |
| F-001-TC2 | `TestExecuteRequestWithRetries_RetryLimits` | core/bifrost_test.go:131 | retry loop stops at `MaxRetries` |
| F-001-TC3 | `TestExecuteRequestWithRetries_NonRetryableErrors` | core/bifrost_test.go:176 | some error classes never retry |
| F-001-TC4 | `TestExecuteRequestWithRetries_RetryableConditions` | core/bifrost_test.go:236 | some error classes always retry |
| F-001-TC5 | `TestCalculateBackoff_ExponentialGrowth` / `_JitterBounds` / `_MaxBackoffCap` | core/bifrost_test.go:314,344,374 | backoff curve shape, jitter, and cap |
| F-001-TC6 | `TestExecuteRequestWithRetries_LoggingAndCounting` | core/bifrost_test.go:514 | attempt count and routing-engine log entries match actual attempts |
| F-001-TC7 | `TestPerKeyFailureStatusCodes` | core/bifrost_test.go:796 | 401/403/429 classified as per-key failures, trigger rotation |
| F-001-TC8 | `TestTransientServerStatusCodes` | core/bifrost_test.go:716 | 5xx/network errors do NOT rotate the key |
| F-001-TC9 | `TestExecuteRequestWithRetries_529RetriesSameKeyWithoutRotation` | core/bifrost_test.go:744 | 529 (overloaded) explicitly excluded from rotation |
| F-001-TC10 | `TestProviderQueue_SendOnClosedChannel_Race` | core/bifrost_test.go:2070 | the "never close pq.queue" design survives a race detector run |
| F-001-TC11 | `TestProviderQueue_IsClosingStateTransition` | core/bifrost_test.go:2173 | `closing` atomic flips exactly once |
| F-001-TC12 | `TestProviderQueue_SignalOnceIdempotent` | core/bifrost_test.go:2220 | `signalClosing` is safe to call more than once |
| F-001-TC13 | `TestProviderQueue_WorkerExitsViaDone` | core/bifrost_test.go:2246 | worker goroutine exits cleanly on shutdown |
| F-001-TC14 | `TestProviderQueue_WorkerDrainSendsErrors` | core/bifrost_test.go:2297 | buffered messages get error responses on shutdown, not silent drops |
| F-001-TC15 | `TestUpdateProvider_StaleProducerReroutes` | core/bifrost_test.go:2462 | in-flight producer transparently re-routes to the replacement queue on update |
| F-001-TC16 | `TestRemoveProvider_BufferedRequestsGetErrors` | core/bifrost_test.go:2837 | removal (not update) errors out buffered requests instead of re-routing |
| F-001-TC17 | `TestChannelMessageHandoffIsExclusive` | core/abandonedstream_test.go:443 | exactly one of claim/abandon wins the handoff race |
| F-001-TC18 | pool-reset test for `releaseChannelMessage` | core/bifrost_test.go:3555 | released message carries no stale request/context/response references |

## Implementation status

| Test case | Status | Evidence |
| --- | --- | --- |
| F-001-TC1..TC18 | `wip — unverified, run go test ./core/... -run <TestName>` | test code exists and is cited above; not executed in this reverse-docs pass (see report — user declined/was not asked to run the live suite in this session) |

## Edge and negative cases

- Queue full with `dropExcessRequests=true` vs `false` (blocking vs dropping) — covered structurally by the enqueue `select`/`default` branches [D: core/bifrost.go:5707-5721], but no dedicated `TestQueueFull*` function name was found in this survey pass — OPEN: is queue-full behavior covered anywhere, or only reachable via load/integration tests outside core/?
- Caller cancellation racing worker claim — `TestChannelMessageHandoffIsExclusive` [D: core/abandonedstream_test.go:443].
- Concurrent provider update racing shutdown drain — `TestUpdateProvider_NoPanicConcurrentAccess`, `TestRemoveProvider_ConcurrentNewProducersDuringShutdown` [D: core/bifrost_test.go:2609, core/bifrost_test.go:2968].

## Out of scope

- Provider-specific conversion correctness (openai/, anthropic/, bedrock/, etc.) — covered in F-003 Provider Implementations' test plan.
- MCP tool execution and connection lifecycle — covered in F-004 MCP Integration's test plan.
- Live end-to-end behaviour against real provider APIs (`make test-core`, `internal/llmtests/`) — a different test tier than the unit tests inventoried here; not run in this pass.

OPEN: is there a dedicated queue-full / backpressure test anywhere in the repo (possibly under `transports/` load tests), or is this path only implicitly exercised?
