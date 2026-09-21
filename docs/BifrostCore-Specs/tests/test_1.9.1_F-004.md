---
title: Test Plan 1.9.1 F-004 — MCP Integration
id: F-004
kind: test
feature: F-004
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Test Plan 1.9.1 F-004 — MCP Integration

> Concrete cases traced back to acceptance criteria.

## Traceability matrix

| Story/AC | Test cases | Level |
| --- | --- | --- |
| F-004-US1 (destructive+non-idempotent never auto-retried) | F-004-TC1, TC2, TC3 | unit |
| F-004-US2 (rotation vs. disable race resolves safely) | F-004-TC4, TC5 | unit |
| (unmapped) Starlark code-mode conversions | F-004-TC6 | unit |

## Test cases

- **F-004-TC1** — `TestExecuteTool_AuthFailureRetry_DestructiveNonIdempotent_SkipsRetry`: destructive+non-idempotent tool, auth-shaped failure → original error surfaces unchanged, no recovery machinery runs [D: core/mcp/auth_retry_test.go:811].
- **F-004-TC2** — `TestExecuteTool_AuthFailureRetry_Shared_DestructiveNonIdempotent_ReconnectsWithoutRetry`: same tool shape on the shared-connection path → background force-refresh + reconnect still runs, only the retry is skipped [D: core/mcp/auth_retry_test.go:689].
- **F-004-TC3** — `TestExecuteTool_AuthFailureRetry_DestructiveButIdempotent_StillRetries`: destructive AND idempotent → retry proceeds (repeated calls have no additional effect) [D: core/mcp/auth_retry_test.go:846].
- **F-004-TC3b** — `TestExecuteTool_AuthFailureRetry_NoAnnotations_SkipsRetry`: no `Annotations` at all → fail-closed, same as explicitly destructive+non-idempotent [D: core/mcp/auth_retry_test.go:875].
- **F-004-TC4** — `TestCloseAndMarkNeedsReauth_PerUserAuth_ReturnsNotApplicable`: per-user-auth clients (no shared connection) → rotation must not error the caller and must not touch entry state [D: core/mcp/clientmanager_test.go:192].
- **F-004-TC5** — `TestCloseAndMarkNeedsReauth_Disabled_IsNoOp`: rotation racing a disable → `DisableClient`'s state is authoritative [D: core/mcp/clientmanager_test.go:223].
- **F-004-TC6** — Starlark codemode conversion suite (`Convert Bool/Dict/Float/Int/List/String/None`, `Convert map/nil/int/float64/bool`) — value marshaling correctness between Go and Starlark [D: core/mcp/codemode/starlark/starlark_test.go:65-186].

## Implementation status

| Test case | Status | Evidence |
| --- | --- | --- |
| F-004-TC1 | wip — unverified, run `make test-mcp TESTCASE=TestExecuteTool_AuthFailureRetry_DestructiveNonIdempotent_SkipsRetry` | not run in this pass |
| F-004-TC2 | wip — unverified, run `make test-mcp TESTCASE=TestExecuteTool_AuthFailureRetry_Shared_DestructiveNonIdempotent_ReconnectsWithoutRetry` | not run in this pass |
| F-004-TC3 | wip — unverified, run `make test-mcp TESTCASE=TestExecuteTool_AuthFailureRetry_DestructiveButIdempotent_StillRetries` | not run in this pass |
| F-004-TC3b | wip — unverified, run `make test-mcp TESTCASE=TestExecuteTool_AuthFailureRetry_NoAnnotations_SkipsRetry` | not run in this pass |
| F-004-TC4 | wip — unverified, run `make test-mcp TESTCASE=TestCloseAndMarkNeedsReauth_PerUserAuth_ReturnsNotApplicable` | not run in this pass |
| F-004-TC5 | wip — unverified, run `make test-mcp TESTCASE=TestCloseAndMarkNeedsReauth_Disabled_IsNoOp` | not run in this pass |
| F-004-TC6 | wip — unverified, run `make test-mcp TYPE=codemode` | not run in this pass |

## Edge and negative cases

- Missing annotations entirely (F-004-TC3b) — the fail-closed default.
- Reconnect racing a disable (F-004-TC5) — ordering/authority conflict, not a value-boundary case.
- Caller cancellation vs. deadline expiry during a reconnect wait — comment-stated at `core/mcp/toolmanager.go:962` but **no test case name was found citing it in survey.md's test list**; this is a coverage hole, not a covered edge case.

OPEN: is this behavior actually tested anywhere, under a name the survey's regex heuristic missed?

## Out of scope

Agent-loop parallel tool execution and the depth-cap loop itself (`agent.go`) have their own test file `core/mcp/agent_test.go`, not enumerated here — this test plan focuses on the auth-retry opt-out and connection-rotation cases survey.md's constraint scan surfaced as rule-likeness ≥6. A follow-up pass should walk `agent_test.go` directly for full agent-loop coverage.
