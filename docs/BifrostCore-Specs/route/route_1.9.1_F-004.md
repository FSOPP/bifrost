---
title: Route 1.9.1 F-004 — MCP Integration
id: F-004
status: draft
owner: TBD
updated: 2026-09-21
---

# Route 1.9.1 F-004 — MCP Integration

> Agent entrypoint: the exact documents to read, in order, before touching this feature.

## Objective

Give an agent picking up MCP-integration work (tool filtering, agent-loop, connection lifecycle, code-mode sandbox) the reversed-from-code baseline before it touches `core/mcp`.

## Required reading (in order)

1. `docs/BifrostCore-Specs/architect/feature_1.9.1_F-004_architect.md` — sequence, failure modes, the connection-state contradiction noted there.
2. `docs/BifrostCore-Specs/data/api-contract_1.9.1_F-004.md` — the `MCPManagerInterface` Go contract (this feature has no HTTP surface of its own).
3. `docs/BifrostCore-Specs/data/data-erd_1.9.1_F-004.md` — the in-memory entities and whitelist semantics.
4. `docs/BifrostCore-Specs/tests/test_1.9.1_F-004.md` — the pinned auth-retry and rotation-race test cases; do not reintroduce a case they already forbid.
5. `docs/BifrostCore-Specs/PRDs/prd_1.9.1_F-004-mcp-integration.md` — stories and the OPEN questions on this feature.

## Guardrails

Do not treat AGENTS.md's "4 levels of MCP tool filtering" claim as fully implemented inside `core/mcp` — this survey found only two whitelist levels (`ToolsToExecute`, `ToolsToAutoExecute`) here; the other levels live in `transports/`. Do not resolve the `clientmanager.go:2090-2096` comment/code state-name contradiction by editing either side without checking with whoever owns that history first — it may be intentional (stale comment) or a real bug.

## Exit criteria

The agent has read the required documents above and, if implementing, has run the cited `make test-mcp` commands and updated the relevant `F-004-T<k>`/`F-004-TC<k>` rows via `docs_flow.py task`.

## Rule file

`rule_1.9.1_F-004.json` — generated; regenerate via `python docs/BifrostCore-Specs/route/rule_1.9.1_F-004.py` if this route's reading list changes.
