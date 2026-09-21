---
title: Domain — MCP Integration
id: DOM-001
kind: domain
feature: F-004
status: draft
owner: TBD
updated: 2026-09-21
---

# Domain — MCP Integration

> Business rules, process and flow in the language of the business.

> Scope note: rule IDs here (`DOM-001-R<k>`) are local to this file, distinct from the hub-wide IDs in `domain_DOM-001-core-engine.md` (which already carries the cross-cutting `DOM-001-R5`/`R6`/`R7` MCP rules pinned from the top-level survey pass — R5/R6 are consistent with this file's R2/R4 below; R7 is flagged CONTRADICTED there and repeated here with the full citation).

## Ubiquitous language

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| MCP client | A configured connection to one Model Context Protocol server, tracked by `clientmanager.go` with a connection state and tool inventory [D: mcp/clientmanager.go] | "MCP server" (the client is Bifrost's side of the connection) |
| Connection state | One of `healthy`, `unstable`, `error`, `pending_verification`, `disabled`, `needs_reauth`, `degraded` — the real `MCPConnectionState` enum [D: schemas/mcp.go — enum definition; contradicts the comment at mcp/clientmanager.go:2090, see Open questions] | "Disconnected"/"Connected" (used in a stale comment, not real enum values) |
| Destructive tool | An MCP tool whose `Annotations.DestructiveHint` is true (or absent — see R3's fail-closed default) | — |
| Idempotent tool | An MCP tool whose `Annotations.IdempotentHint` is true; repeated calls have no additional effect | — |
| Agent loop | The multi-turn tool-calling loop in `agent.go` that keeps calling tools until the model stops asking or `maxAgentDepth` is hit | "ReAct loop" (not the codebase's own term) |

## Actors

- The engine (F-001) / HTTP transport (out of `core/` scope) — invokes `MCPManagerInterface` methods.
- `ClientConnectionChecker` — the sole authority over connection-state transitions; a live tool call's success or failure never mutates state itself. [D: mcp/connectionchecker.go:9-16]
- The MCP tool server — the external system a client connects to.
- An admin/operator — calls `DisableClient`/`EnableClient`, whose effect on state takes precedence over an in-flight rotation (R4).

## Business rules

1. **DOM-001-R1** — Connection state is mutated only by `ClientConnectionChecker`; a live tool call's own success or failure never touches `State`. The checker's own doc comment states it is "Bifrost's SOLE authority over these state transitions." [D: mcp/connectionchecker.go:9-16]
2. **DOM-001-R2** — A destructive AND non-idempotent tool must never be auto-retried on an auth-shaped failure; the original error surfaces unchanged. Shared-connection clients still run background force-refresh + reconnect regardless, so the connection heals even though the specific call is not retried. [D: mcp/toolmanager.go:835-867, 912-921]
3. **DOM-001-R3** — Fail-closed default: a tool with no `Annotations` at all is treated as destructive AND non-idempotent (both MCP-spec hints optional, so this is common) — same retry-skip as R2, never defaulted to "safe to retry." [D: mcp/toolmanager.go:835-864]
4. **DOM-001-R4** — `DisableClient`'s state is authoritative over a rotation (`CloseAndMarkNeedsReauth`) that started before the disable: a rotation racing a disable must not resurrect the client into `needs_reauth`. [D: mcp/clientmanager_test.go:223]
5. **DOM-001-R5** — A canceled caller (vs. a deadline expiry) on an in-flight reconnect wait must not park for the remaining budget; the reconnect itself keeps running in the background regardless of the canceling caller. [D: mcp/toolmanager.go:962]
6. **DOM-001-R6** — On a per-user-OAuth auth-required error surfacing from any auto-executed tool call mid-batch, the whole agent loop aborts with a single 401 `mcp_auth_required` error (`authRequiredOnce` ensures only the first is surfaced), rather than continuing the loop. [D: mcp/agent.go:306-345]

## Process flow

D: see `architect/feature_1.9.1_F-004_architect.md`'s Sequence section for the full cited agent-loop and auth-recovery call chains. Restated at domain level:
1. Agent loop extracts tool calls from the current response; stops if none. [D: mcp/agent.go:168-173]
2. Splits into auto-executable vs. not, applying R2/R3's retry-gate logic when a call later fails on auth.
3. Non-auto-executable tools halt the loop and return unexecuted alongside prior results.
4. A per-user-OAuth failure anywhere in the batch aborts the whole loop (R6).

## Invariants

- Connection state changes only inside `ClientConnectionChecker` (R1) — never as a side effect of a tool call.
- A destructive+non-idempotent tool call is never repeated by this package's own retry logic (R2, R3).
- `DisableClient` always wins a race against a concurrent rotation (R4).

## Implementation status

| Rule | Status | Evidence |
| --- | --- | --- |
| DOM-001-R1 | wip — unverified, no dedicated test name surfaced beyond the doc comment | `mcp/connectionchecker.go:9-16` |
| DOM-001-R2 | wip — unverified, run `go test ./core/mcp/... -run TestExecuteTool_AuthFailureRetry_Shared_DestructiveNonIdempotent_ReconnectsWithoutRetry` (mock-based, no live API per AGENTS.md) | `mcp/auth_retry_test.go:689` |
| DOM-001-R3 | wip — unverified, run `go test ./core/mcp/... -run TestExecuteTool_AuthFailureRetry_NoAnnotations_SkipsRetry` | `mcp/auth_retry_test.go:875` |
| DOM-001-R4 | wip — unverified, run `go test ./core/mcp/... -run TestCloseAndMarkNeedsReauth_Disabled_IsNoOp` | `mcp/clientmanager_test.go:223` |
| DOM-001-R5 | wip — unverified, no dedicated test name surfaced in survey — real coverage hole, not just unrun | `mcp/toolmanager.go:962` (comment only) |
| DOM-001-R6 | wip — unverified, no dedicated test name surfaced in survey | `mcp/agent.go:306-345` |

None run in this session (`make test-mcp` is mock-based and does not hit live APIs per AGENTS.md, but was not run unattended here either).

## Open questions

- OPEN, contradiction not just unknown: the comment at `mcp/clientmanager.go:2090` claims a new client "Initialize[s] State to Disconnected... transitions to Connected only on success," but the code on that line sets `State: schemas.MCPConnectionStateUnstable`, and neither `Disconnected` nor `Connected` exist in the real `MCPConnectionState` enum (real values: `healthy`, `unstable`, `error`, `pending_verification`, `disabled`, `needs_reauth`, `degraded`). This is a stale/wrong comment next to live code, not a domain rule — do not implement against the comment's wording.
- OPEN: R5 (cancellation-vs-deadline) has no test name found anywhere in this survey pass — is it actually covered by an integration/load test outside `core/mcp/`, or is this a real gap?
- OPEN: AGENTS.md's gotcha #15 claims a 4-level MCP tool filter hierarchy (global/client/tool/per-request); `core/mcp` itself only shows evidence of 2 of those levels (`ToolsToExecute`, `ToolsToAutoExecute`) — the other 2 likely live in `transports/`, unverified from this module alone.
- OPEN: is `maxAgentDepth` a documented product limit (cost/SLO control) or an incidental safety valve? No config default is visible in `core/mcp` for what operators actually set.
