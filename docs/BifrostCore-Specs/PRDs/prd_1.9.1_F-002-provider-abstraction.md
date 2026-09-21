---
title: PRD 1.9.1 F-002 — Provider Abstraction
id: F-002
kind: prd
feature: F-002
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# PRD 1.9.1 F-002 — Provider Abstraction

> Feature-level requirements: what and why, never how.

## Summary

I: `core/schemas` exists so that every AI provider Bifrost supports can be added, tested and swapped behind one contract, without the engine (F-001) or any provider (F-003) needing to know about the others — basis: a single `Provider` Go interface (30 methods) is the only type every one of the 20+ provider packages implements, and every request the engine dispatches is one of the `Bifrost*Request` shapes this package defines [D: core/schemas/provider.go:681-800; core module layout — 543 provider files vs 130 schema files].

## User stories

- **F-002-US1**: As a provider implementer, I implement the `Provider` interface once and my provider works with every operation the engine can dispatch (chat, responses, embeddings, batch, files, images, video, etc.), including operations I choose not to support, so that adding a new provider does not require touching the engine. [I: inferred from the interface's method count and the "not supported" convention — basis: `providers/groq/groq.go:88-90` returns a typed error rather than the method being absent, which only makes sense if the engine always calls through the same interface regardless of provider capability]
- **F-002-US2**: As the engine, I can detect at runtime whether a specific provider supports an optional capability (Responses lifecycle verbs, namespace tools, WebSocket mode) via a type assertion, so that I don't hard-code a provider allowlist for these features. [D: core/schemas/provider.go:802-837 — three separate optional interfaces, each documented as "checked via type assertion in core dispatch"]
- **F-002-US3**: As a plugin author, I can attach request-scoped state to `BifrostContext` and read it later in the pipeline, without the engine's own reserved state (retry count, fallback index, selected key) being overwritable by my plugin. [D: core/schemas/context.go:19-45 reserved-key set; core/schemas/context.go:480-484 silent-drop guard]
- **F-002-US4**: As a plugin author, I implement one of four typed interfaces (`LLMPlugin`/`MCPPlugin`/`HTTPTransportPlugin`/`ObservabilityPlugin`) and get a guaranteed pre/post-hook execution order (registration order forward, reverse on the way back), so that my plugin composes predictably with others. [D: core/schemas/plugin.go:174-203 doc comment; core/schemas/plugin.go:318-477 interface definitions]

## Acceptance criteria

- F-002-US1: Given a new provider package implementing all 30 `Provider` methods, when the engine calls any of them, then the call succeeds or returns a typed `*BifrostError` — never a compile error or a missing-method panic. [D: Go's static interface satisfaction — the engine can only hold a value that already implements every method]
- F-002-US2: Given a provider that does not implement `ResponsesLifecycleProvider`, when the engine attempts `ResponsesRetrieve`, then the type assertion fails and the caller receives `unsupported_operation` rather than a nil-pointer dereference. [I: inferred from the comment "providers that do not implement it return unsupported_operation" — basis: core/schemas/provider.go:804]
- F-002-US3: Given `blockRestrictedWrites` is set on a context, when a plugin calls `SetValue(BifrostContextKeyFallbackIndex, ...)`, then the write is silently dropped and the engine's own value is preserved. [D: core/schemas/context.go:480-484, tested at context_test.go per survey's 18-function count]
- F-002-US4: Given plugins A then B registered (in that order), when a request runs, then `PreLLMHook` fires A→B and `PostLLMHook` fires B→A. [D: core/schemas/plugin.go:171 doc comment "PreHooks are executed in the order they are registered... PostHooks... reverse order"]

## Implementation status

| Story | Status | Evidence |
| --- | --- | --- |
| F-002-US1 | wip — unverified, run `go build ./core/...` | F-002-T1 |
| F-002-US2 | wip — unverified, run `go vet ./core/schemas/...` | F-002-T1 |
| F-002-US3 | wip — unverified, run `go test ./core/schemas/... -run TestBifrostContext` | F-002-T2, F-002-TC3 |
| F-002-US4 | wip — unverified, run `go test ./core/schemas/... -run TestPlugin` | F-002-T3, F-002-TC5 |

## Scope boundaries

Out of scope: HTTP-level request/response translation (transports, not surveyed in this pass), provider-specific converter logic (F-003), MCP tool-calling semantics (F-004), the engine's routing/retry/fallback decision logic (F-001) — this feature is the *shape* those other features operate on, not the logic that operates on it.

## Dependencies

F-001 (Core Engine — the sole caller of the `Provider` interface and owner of `BifrostContext` lifecycle), F-003 (every concrete `Provider` implementer), F-004 (`schemas/mcp.go` types feed the MCP integration, cross-referenced not owned here).

## Metrics

No success metric for this feature is expressed anywhere in the code — interface stability and provider-onboarding friction are not measured quantities in this repository.

- OPEN: is there a target for "time to add a new provider" or "percentage of `Provider` methods implemented per provider" tracked anywhere outside this codebase (e.g. in an issue tracker)?
