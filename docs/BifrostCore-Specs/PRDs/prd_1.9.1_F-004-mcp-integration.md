---
title: PRD 1.9.1 F-004 — MCP Integration
id: F-004
kind: prd
feature: F-004
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# PRD 1.9.1 F-004 — MCP Integration

> Feature-level requirements: what and why, never how.

## Summary

I: MCP Integration turns Bifrost from a static chat-completion gateway into a tool-calling agent runtime — it manages MCP server connections, filters and executes tools on the model's behalf across multiple turns, and does so with safety opt-outs so an unreliable connection cannot cause a destructive action twice — basis: the shape of `agent.go`'s loop, `toolmanager.go`'s retry-opt-out gate, and `clientmanager.go`'s connection lifecycle, taken together [D: core/mcp/agent.go, core/mcp/toolmanager.go, core/mcp/clientmanager.go].

## User stories

- **F-004-US1**: As an operator running MCP tools through Bifrost, a destructive tool that is not idempotent is never automatically retried after an auth failure, so a transient credential hiccup cannot cause the tool's side effect twice — inferred from `TestExecuteTool_AuthFailureRetry_DestructiveNonIdempotent_SkipsRetry` and its sibling cases [D: core/mcp/auth_retry_test.go:811, 689, 846, 875].
- **F-004-US2**: As an operator rotating MCP client credentials, a rotation that races an admin disabling the same client does not resurrect it into a re-auth-needed state — inferred from `TestCloseAndMarkNeedsReauth_Disabled_IsNoOp` [D: core/mcp/clientmanager_test.go:223].
- **F-004-US3**: As a caller of the agent loop, canceling my request does not need to wait out a background reconnect's full budget — inferred from the comment-stated rule at `core/mcp/toolmanager.go:962` (no directly-named test found for it — see the coverage gap in `tests/test_1.9.1_F-004.md`).

## Acceptance criteria

- **US1**: Given a tool annotated (or defaulted, per spec, to) destructive+non-idempotent, when a call to it fails with an auth-shaped error, then the retry is skipped and the original error surfaces unchanged [D: core/mcp/toolmanager.go:859-864].
- **US2**: Given a client in `Disabled` state, when a credential-rotation call races in, then the client's state remains `Disabled`, not `needs_reauth` [D: core/mcp/clientmanager_test.go:223].
- **US3**: OPEN — no test name confirms this criterion end-to-end; the criterion is inferred from a code comment only.

## Implementation status

| Story | Status | Evidence |
| --- | --- | --- |
| F-004-US1 | wip — unverified, run `make test-mcp TESTCASE=TestExecuteTool_AuthFailureRetry_DestructiveNonIdempotent_SkipsRetry` | F-004-TC1, TC2, TC3, TC3b; F-004-T1 |
| F-004-US2 | wip — unverified, run `make test-mcp TESTCASE=TestCloseAndMarkNeedsReauth_Disabled_IsNoOp` | F-004-TC5; F-004-T2 |
| F-004-US3 | todo — no test case identified this pass | none found |

## Scope boundaries

Out of scope: the HTTP-level MCP endpoints (`transports/bifrost-http/handlers/mcp*.go`) and MCP client credential persistence (`framework/configstore/`) — both outside `core/`. The agent loop's provider-side chat/responses request/response conversion is F-002/F-003's concern, not this feature's.

## Dependencies

F-002 (Provider Abstraction) — `schemas.BifrostContext`, `schemas.ChatTool`, `schemas.BifrostError` types this feature consumes. F-003 (Provider Implementations) — the actual LLM call inside the agent loop (`makeReq`) is supplied by the caller, not owned here.

## Metrics

OPEN: no success metric (tool-call latency SLO, retry-success rate, connection-uptime target) is expressed anywhere in this package. This is a genuine gap in what the organisation has written down, not an oversight in this document.
