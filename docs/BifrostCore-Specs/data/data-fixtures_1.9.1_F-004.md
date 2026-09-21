---
title: Data Fixtures 1.9.1 F-004 — MCP Integration
id: F-004
status: draft
owner: TBD
updated: 2026-09-21
---

# Data Fixtures 1.9.1 F-004 — MCP Integration

> The test data this feature is implemented and verified against, and what each fixture is for.

## Fixture sets

No JSON/YAML fixture files exist under `core/mcp` — tests build `schemas.MCPClientState`/tool-annotation values as Go literals inline in `_test.go` files, not from external fixture data [D: survey — no fixture files found under core/mcp by extension scan]. Representative in-code "fixture" shapes, by scenario:

| Set ID | Entities | Scenario | Test cases |
| --- | --- | --- | --- |
| F-004-FX1 | Tool with `Annotations{ReadOnlyHint:false, DestructiveHint:true, IdempotentHint:false}` | Destructive + non-idempotent → retry skipped | `TestExecuteTool_AuthFailureRetry_*_SkipsRetry` [D: mcp/auth_retry_test.go:811, 875] |
| F-004-FX2 | Tool with `Annotations{DestructiveHint:true, IdempotentHint:true}` | Destructive but idempotent → retry still runs | `TestExecuteTool_AuthFailureRetry_DestructiveButIdempotent_StillRetries` [D: mcp/auth_retry_test.go:846] |
| F-004-FX3 | Tool with `Annotations: nil` | No hints at all → fail-closed, treated as destructive+non-idempotent | `TestExecuteTool_AuthFailureRetry_NoAnnotations_SkipsRetry` [D: mcp/auth_retry_test.go:875] |
| F-004-FX4 | `MCPClientState{ExecutionConfig.AuthType: per_user_oauth / per_user_headers}` | Per-user-auth clients hold no shared connection — rotation must be a no-op, not an error | `TestCloseAndMarkNeedsReauth_PerUserAuth_ReturnsNotApplicable` [D: mcp/clientmanager_test.go:192] |
| F-004-FX5 | `MCPClientState{State: Disabled}` racing a rotation call | `DisableClient` state must win over an in-flight rotation | `TestCloseAndMarkNeedsReauth_Disabled_IsNoOp` [D: mcp/clientmanager_test.go:223] |

## Fixture file

`fixtures/fixtures_1.9.1_F-004.json` is left as the scaffold's empty stub — there is no external fixture file to mirror. OPEN: should this hub instead capture the Go-literal shapes above as a JSON fixture file for cross-tool reuse, or is inline-per-test the intended convention here?

## Encoded invariants

The FX1–FX3 set exists specifically to exercise the fail-closed default: MCP annotations are optional per spec, so an unannotated tool is the common case, and the test suite deliberately proves that common case is *not* treated as safe-to-retry [D: mcp/toolmanager.go:835-841].

## Determinism rules

N/A — no external fixture data; each test constructs its own literal, so determinism is inherent to the Go test function itself. OPEN: not verified in this pass whether any of these tests use real wall-clock reads (`time.Now()`) that could make them flaky — `connectionchecker_test.go:260`'s "generation 5" test name suggests a generation-counter approach was chosen specifically to avoid timing dependence, but this was not verified directly.

## Loading

Not applicable — no store to load into or reset; tests construct `ToolsManager`/`ClientManager` instances directly per-test.

## Traceability

Serves F-004-TC1–TC6 in `tests/test_1.9.1_F-004.md`.
