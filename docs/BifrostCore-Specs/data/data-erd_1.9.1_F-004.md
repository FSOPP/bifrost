---
title: Data Model 1.9.1 F-004 — MCP Integration
id: F-004
status: draft
owner: TBD
updated: 2026-09-21
---

# Data Model 1.9.1 F-004 — MCP Integration

> The slice of the data model this feature reads and writes, at field precision.

## Scope

`core/mcp` owns two in-memory structures, no persisted database entities (no DB access from this package — `core/mcp/interface.go:77`'s own doc comment: "core/mcp has no DB access; this is the seam the transport layer persists through") [D: core/mcp/interface.go:77]:

| Entity | Own / Read / Write |
| --- | --- |
| `schemas.MCPClientState` | Owns (in-memory, per-process) [D: core/schemas/mcp.go:947-961] |
| `schemas.MCPClientConfig` | Reads (supplied by caller at `AddClient`/`UpdateClient`); does not persist it [D: core/mcp/interface.go:82, 93] |

Anything about how a client config is persisted across restarts (config store, file, DB row) is out of bounds — that lives in `framework/configstore/`, outside `core/`.

## Feature ERD

See `schema/erd_1.9.1_F-004.puml`. Both entities are process-local; no foreign-key relation to a persisted store exists in this package.

## Field definitions

| Entity | Field | Type | Constraint | Notes |
| --- | --- | --- | --- | --- |
| `MCPClientState` | `Name` | String | — | [D: core/schemas/mcp.go:947] |
| `MCPClientState` | `State` | `MCPConnectionState` | one of `healthy`, `unstable`, `error`, `pending_verification`, `disabled`, `needs_reauth`, `degraded` | `degraded` is a read-time aggregate, never itself assigned [D: core/schemas/mcp.go:834-888, 947] |
| `MCPClientState` | `ToolMap` | `map[string]schemas.ChatTool` | last-known-good, kept (not cleared) across a failed reconnect | [D: core/mcp/clientmanager.go:2075-2081] |
| `MCPClientState` | `ToolNameMapping` | `map[string]string` | — | [D: core/schemas/mcp.go:961] |
| `MCPClientConfig` | `ToolsToExecute` | `WhiteList` | `["*"]`=all, `[]`=none (deny-by-default), named list=include-only | [D: core/schemas/mcp.go:509-511] |
| `MCPClientConfig` | `ToolsToAutoExecute` | `WhiteList` | same shape, gates auto-execution specifically | [D: core/schemas/mcp.go:515-518] |
| `MCPClientConfig` | `IsPingAvailable` | `*bool` | nil/true=ping, false=listTools for health checks | [D: core/schemas/mcp.go:522] |

I: `WhiteList` is a named slice type with `IsEmpty()`/`IsUnrestricted()` helper methods (called from `core/mcp/agent.go:499,506`) — basis: call sites imply the methods exist and the comments at `core/schemas/mcp.go:511-518` state the three-way semantics, though the type's own declaration was not read in this pass [D: core/mcp/agent.go:499-518].

## New and changed entities

This feature does not modify the master schema — no migration, no new persisted table. `data-master-erd.md`'s registry should list `MCPClientState`/`MCPClientConfig` as in-memory-only, owned by `core/mcp`, if the master registry tracks non-persisted entities at all (OPEN, see below).

## Migrations

N/A — no database, no migration files under `core/mcp`.

## Traceability

OPEN: no `DOM-nnn-R<k>` rule currently cites `ToolsToExecute`/`ToolsToAutoExecute` in `ddd/domain_DOM-001-core-engine.md` — the deny-by-default whitelist semantics is a strong candidate for a promoted domain rule; flagging rather than promoting it myself, since that document is owned by a different pass of this hub.
