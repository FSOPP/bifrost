---
title: Feature Architecture 1.9.1 F-004 — MCP Integration
id: F-004
kind: architecture
feature: F-004
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Feature Architecture 1.9.1 F-004 — MCP Integration

> Low-level design for one feature: contracts, schema, sequence, failure modes.

## Design summary

`core/mcp` turns a static chat model into a tool-calling agent over the Model Context Protocol: it manages MCP client connections and their tool inventories (`clientmanager.go`), gates and executes individual tool calls including a Starlark code-mode sandbox (`toolmanager.go`, `codemode/starlark/`), and runs the multi-turn agent loop that keeps calling tools until the model stops asking for them or a depth cap is hit (`agent.go`) [D: core/mcp/agent.go:1, core/mcp/clientmanager.go:1, core/mcp/toolmanager.go:1].

I: the package is designed so a live tool call's success or failure never mutates client connection state — only the periodic `ClientConnectionChecker` does — basis: the checker's own doc comment states it is "Bifrost's SOLE authority over these state transitions. Nothing else — a live tool call succeeding or failing — ever touches State" [D: core/mcp/connectionchecker.go:9-16]. This rules out state flapping from a single flaky call.

## API contracts

`core/mcp` exposes no HTTP endpoints itself — inbound HTTP for MCP client CRUD and tool execution lives in `transports/bifrost-http/handlers/mcp*.go`, outside this feature's scope [D: survey: 0 endpoints found under core/]. The real contract for this feature is the Go interface `MCPManagerInterface` (`core/mcp/interface.go:15-133`), which the HTTP/SDK layers call against: tool operations (`AddToolsToRequest`, `GetAvailableTools`), agent-mode operations (`CheckAndExecuteAgentForChatRequest`, `CheckAndExecuteAgentForResponsesRequest`), single-tool execution (`ExecuteChatTool`, `ExecuteResponsesTool`), and client lifecycle (`AddClient`, `RemoveClient`, `UpdateClient`, `ReconnectClient`, `CloseAndMarkNeedsReauth`, `DisableClient`, `EnableClient`) [D: core/mcp/interface.go:15-133]. Full method table and payload shapes: `data/api-contract_1.9.1_F-004.md`.

OPEN: which of these interface methods are reachable from the HTTP transport versus only from the Go SDK path — that routing lives in `transports/bifrost-http/handlers/mcp.go`, out of this survey's scope (core/ only).

## Data model

This feature owns no persisted entities (core/mcp has no DB access — `SetToolsChangeCallback`'s own doc comment states "core/mcp has no DB access; this is the seam the transport layer persists through" [D: core/mcp/interface.go:77]). It owns two in-memory structures: `schemas.MCPClientState` (per-client connection + tool map, `core/schemas/mcp.go:947-980`) and the client's `ToolMap`/`ToolNameMapping`. Field detail: `data/data-erd_1.9.1_F-004.md`.

## Sequence

**Agent loop (happy path, `agent.go:140-397` `executeAgent`):**
1. Adapter (`chatAPIAdapter` or `responsesAPIAdapter`) supplies the initial response and conversation history [D: core/mcp/agent.go:46-50, 99-103].
2. Loop while `depth < maxAgentDepth`: extract tool calls from the current response; if none, stop [D: core/mcp/agent.go:168-173].
3. Split tool calls into auto-executable vs. non-auto-executable, resolving each by client (`clientManager.GetClientForTool`) and its `ExecutionConfig` (`canAutoExecuteTool`), with special-cased code-mode tools (`listToolFiles`/`readToolFile`/`getToolDocs` always auto-executable; `executeToolCode` auto-executable only if every tool call extracted from the submitted code is in the client's `ToolsToAutoExecute` allow-list) [D: core/mcp/agent.go:179-274].
4. Auto-executable tools run in parallel goroutines, each on its own derived `BifrostContext` tagged with a fresh `BifrostContextKeyMCPLogID` [D: core/mcp/agent.go:286-297]; a per-user OAuth auth-required error from any of them aborts the whole loop with a 401 `mcp_auth_required` error rather than continuing [D: core/mcp/agent.go:308-345].
5. Any non-auto-executable tools stop the loop immediately and are returned to the caller unexecuted, alongside whatever was already auto-executed this and prior iterations [D: core/mcp/agent.go:362-372].
6. Otherwise a new LLM request is built from the updated conversation history and depth increments [D: core/mcp/agent.go:374-392].

**Single tool execution with auth-failure recovery (`toolmanager.go` `attemptAuthFailureRecovery`, called from `executeToolInternal`):**
1. On an auth-shaped failure, look up the tool's MCP annotations; fail closed on missing hints (`destructiveHint` defaults `true`, `idempotentHint` defaults `false` — the MCP spec's own defaults, not this package's Go zero-values) [D: core/mcp/toolmanager.go:835-864].
2. If the tool is destructive AND not idempotent, `retryOptedOut = true` — no auto-retry of the call itself [D: core/mcp/toolmanager.go:859-864].
3. Shared-connection clients still always run background force-refresh + reconnect regardless of `retryOptedOut`, so the connection heals even when the specific call is not retried; only the retry step is gated [D: core/mcp/toolmanager.go:866-867, 912-921].
4. Per-call-connection clients: if `retryOptedOut`, return immediately without retrying (no connection to heal in the per-call model) [D: core/mcp/toolmanager.go:870-872].

**Periodic connection health (`connectionchecker.go`):** one ticker per client does both liveness checking and tool-discovery refresh, replacing the former separate health monitor and tool syncer; interval adapts between `DefaultConnectionCheckInterval` (Healthy) and `UnstableConnectionCheckInterval`=10s (Unstable) [D: core/mcp/connectionchecker.go:1-40].

## Failure modes

| Failure | Detection | Behaviour | Recovery |
| --- | --- | --- | --- |
| Tool call returns per-user OAuth auth-required error, mid-parallel-batch | `errors.As(toolErr, &authErr)` in the auto-exec goroutine | Whole agent loop aborts with 401 `mcp_auth_required`, `authRequiredOnce` ensures only the first such error is surfaced | Caller must complete OAuth and retry the original request [D: core/mcp/agent.go:306-345] |
| Destructive, non-idempotent tool call fails with an auth-shaped error | `attemptAuthFailureRecovery`'s annotation check | Retry of the call itself is skipped (`retryOptedOut`); shared connections still get background reconnect | Original error surfaces to caller; next call on a healed connection may succeed [D: core/mcp/toolmanager.go:830-864] |
| Client dial fails on reconnect (close-first path) | `existingClient` branch in `AddClient`/reconnect | State set to `MCPConnectionStateUnstable`, `Conn = nil`, `ConnGeneration++`; last-known-good `ToolMap`/`ToolNameMapping` is left in place, not cleared | Periodic checker keeps retrying at the Unstable interval until it heals or the caller disables the client [D: core/mcp/clientmanager.go:2075-2103] |
| Caller cancels an in-flight reconnect wait (vs. deadline expiry) | `toolmanager.go:962`'s comment-stated distinction | A canceled request must not park for the remaining budget | Reconnect keeps running in the background regardless of the canceling caller [D: core/mcp/toolmanager.go:962] |
| Rotation (`CloseAndMarkNeedsReauth`) races an admin `DisableClient` call | `TestCloseAndMarkNeedsReauth_Disabled_IsNoOp` | `DisableClient`'s state is authoritative; a rotation started before the disable must not resurrect the client into `needs_reauth` | No-op; state stays Disabled [D: core/mcp/clientmanager_test.go:223] |

## Observability

OPEN: no metrics/log-event/trace-span emission list is stated in code as a feature contract — debug/warn log calls exist throughout (`a.logger.Debug(...)`, `m.logger.Warn(...)`) but no survey-extractable event schema. survey.md's "Events / topics" section found only 5 declared-but-unused message-string literals repo-wide, none in `core/mcp` — this feature's runtime signals are ad hoc log lines, not a structured event contract [D: survey.md Events/topics section].

## Traceability

Satisfies: F-004-US1 (auth-failure retry never repeats a destructive non-idempotent side effect), F-004-US2 (a canceled caller does not block on a background reconnect) — see `PRDs/prd_1.9.1_F-004-mcp-integration.md`. No `DOM-nnn` rule is filed against this feature in `ddd/domain_DOM-001-core-engine.md`; the destructive/idempotent retry-gate is a strong domain-rule candidate that document's owner should consider promoting.

OPEN: is the agent loop's `maxAgentDepth` cap itself a documented product limit (SLO/cost control) or an incidental safety valve? No comment or config default is visible in this file for what value operators actually set.
