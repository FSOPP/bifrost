---
title: API Contract 1.9.1 F-004 — MCP Integration
id: F-004
status: draft
owner: TBD
updated: 2026-09-21
---

# API Contract 1.9.1 F-004 — MCP Integration

> The wire contract for this feature — the readable companion to its OpenAPI and AsyncAPI files.

## Surface summary

`core/mcp` is a Go library, not an HTTP service: the survey of `core/` found 0 HTTP endpoints [D: survey.md "HTTP surface: none found"]. The wire-level MCP client/tool HTTP endpoints (add client, list clients, execute tool over HTTP, etc.) are defined in `transports/bifrost-http/handlers/mcp*.go`, outside this feature's scope (core/ only). What this document derives instead is the **Go interface contract** `MCPManagerInterface` (`mcp/interface.go:15-133`) that any transport or SDK caller must code against — this is the real, stable surface this feature guarantees [D: mcp/interface.go:15-133]. `schema/openapi_1.9.1_F-004.json` and `schema/asyncapi_1.9.1_F-004.json` are therefore marked N/A below rather than fabricated.

## Endpoints

N/A — no HTTP endpoints in `core/mcp`. Method table for the Go contract instead:

| Method | Purpose | Returns |
| --- | --- | --- |
| `AddToolsToRequest(ctx, req)` | Injects available MCP tools into an outgoing request | `*schemas.BifrostRequest` [D: mcp/interface.go:18] |
| `GetAvailableTools(ctx)` | Lists tools visible in this context | `[]schemas.ChatTool` [D: mcp/interface.go:21] |
| `CheckAndExecuteAgentForChatRequest` / `...ForResponsesRequest` | Runs the multi-turn agent loop for Chat / Responses API | final response or `*schemas.BifrostError` [D: mcp/interface.go:36-50] |
| `ExecuteChatTool` / `ExecuteResponsesTool` | Executes one tool call through the plugin gate | `*schemas.ChatMessage` / `*schemas.ResponsesMessage` [D: mcp/interface.go:55-56] |
| `AddClient` / `RemoveClient` / `UpdateClient` / `UpdateClientCredentials` / `ReconnectClient` / `CloseAndMarkNeedsReauth` / `DisableClient` / `EnableClient` | Client lifecycle | `error` [D: mcp/interface.go:82-111] |
| `VerifyHeadersConnection` / `VerifyPerUserOAuthConnection` | Test-connect without persisting | tool map + name mapping + `error` [D: mcp/interface.go:113-121] |

## Events

Empty — no publish/subscribe channels in `core/mcp`. survey.md's repo-wide event scan found only 5 declared message-string literals, none in `core/mcp` (the closest, `exchange` at `schemas/mcp.go:56`, is unused and belongs to F-002's schema layer) [D: survey.md Events/topics section].

## Error model

Tool-call errors surface as `*schemas.BifrostError`; the one MCP-specific shape observed is the per-user OAuth case: `IsBifrostError: true`, `StatusCode: 401`, `Error.Type: "mcp_auth_required"`, carrying `ExtraFields.MCPAuthRequired` [D: mcp/agent.go:330-345]. OPEN: no other MCP-specific error codes/types are enumerated in one place in this package — the rest fall through to the generic `*schemas.BifrostError` shape from `schemas/`.

## Versioning and compatibility

OPEN: no version-negotiation or deprecation policy is stated in code for this Go interface; a breaking signature change to `MCPManagerInterface` would be caught only by the `var _ MCPManagerInterface = (*MCPManager)(nil)` compile-time assertion at `mcp/interface.go:136`, not by any documented compatibility contract.

## Spec files

`schema/openapi_1.9.1_F-004.json` and `schema/asyncapi_1.9.1_F-004.json`: N/A, left as generated empty stubs — this feature has no HTTP or event wire contract of its own. Entity shapes referenced above are `$ref`'d from `data/schema/schemas.json`, per hub convention.

## Traceability

Satisfies F-004-US1, F-004-US2 (see `PRDs/prd_1.9.1_F-004-mcp-integration.md`).

OPEN: should the HTTP-level MCP contract (transports/bifrost-http/handlers/mcp*.go) get its own feature/document in a future pass, so this hub's API-contract layer isn't silently incomplete for MCP as a whole?
