---
title: Tasks 1.9.1 F-004 — MCP Integration
id: F-004
kind: tasks
feature: F-004
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Tasks 1.9.1 F-004 — MCP Integration

> Ordered, dependency-aware implementation tasks — plan only, no code.

> As-built inventory — this feature is already shipped code, so every row below records what exists, not what to plan.

## Task list

| Task ID | Description | Depends-on | Artifact | Done-when | Estimate | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F-004-T1 | Auth-failure retry opt-out for destructive/non-idempotent tools | — | `mcp/toolmanager.go:822-864` | F-004-TC1, TC2, TC3, TC3b all pass | done (as-built) | wip — Code exists, tests exist (auth_retry_test.go), suite not run in this pass — run: make test-mcp TESTCASE=TestExecuteTool_AuthFailureRetry_DestructiveNonIdempotent_SkipsRetry |
| F-004-T2 | Client rotation vs. disable-race authority ordering | — | `mcp/clientmanager.go` `CloseAndMarkNeedsReauth`/`DisableClient` | F-004-TC4, TC5 pass | done (as-built) | wip — Code exists, tests exist (clientmanager_test.go), suite not run in this pass — run: make test-mcp TESTCASE=TestCloseAndMarkNeedsReauth_Disabled_IsNoOp |
| F-004-T3 | Multi-turn agent loop with auto/non-auto tool split and code-mode gating | — | `mcp/agent.go:140-397` | `mcp/agent_test.go` suite passes (not itemized here — see Out of scope) | done (as-built) | wip — Code exists, tests exist (agent_test.go), suite not run in this pass — run: make test-mcp TYPE=agent |
| F-004-T4 | Starlark code-mode sandbox (execute/list/read/getdocs) value conversion | — | `mcp/codemode/starlark/*.go` | F-004-TC6 passes | done (as-built) | wip — Code exists, tests exist (starlark_test.go), suite not run in this pass — run: make test-mcp TYPE=codemode |
| F-004-T5 | Periodic connection health/tool-sync checker (single ticker, adaptive interval) | — | `mcp/connectionchecker.go` | no test case name identified in this pass (OPEN) | done (as-built) | wip — Code exists, no test case name identified for the checker itself in this pass |

## Execution order

Not applicable as a build sequence — all five are already-shipped, independently owned units of `core/mcp` with no build-order dependency recorded between them in this pass.

## Definition of done

Per `status-model.md`: `done` requires the cited test command run in this environment with a passing result recorded in the note. None of these rows have been run in this pass — see `tasks_1.9.1_F-004.md` state transitions below.
