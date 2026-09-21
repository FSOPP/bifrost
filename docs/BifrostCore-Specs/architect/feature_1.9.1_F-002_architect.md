---
title: Feature Architecture 1.9.1 F-002 — Provider Abstraction
id: F-002
kind: architecture
feature: F-002
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Feature Architecture 1.9.1 F-002 — Provider Abstraction

> Low-level design for one feature: contracts, schema, sequence, failure modes.

## Design summary

I: `core/schemas` is the type-contract layer the rest of `core` compiles against, not a runtime component of its own — basis: it exports no `main`, starts no goroutine of its own accord (aside from `BifrostContext.watchCancellation`, spawned per-context, not per-package), and every other module (`providers/`, `mcp/`, `network/`, the engine in `core/schemas/bifrost.go`/`inference.go`) imports it [D: core/go.mod:1]. The package defines three things: (1) the `Provider` interface all 20+ providers implement (`core/schemas/provider.go:681-800`), (2) `BifrostContext`, a custom `context.Context` with thread-safe mutable values and a reserved-key write guard (`core/schemas/context.go:77-94`), and (3) the plugin interfaces (`LLMPlugin`/`MCPPlugin`/`HTTPTransportPlugin`/`ObservabilityPlugin`, `core/schemas/plugin.go:213-477`) plus one `Bifrost*Request`/`Bifrost*Response` struct pair per operation family (chat, responses, embedding, images, batch, files, videos, containers, cached contents, speech, transcription, passthrough — 129 top-level `Bifrost*` structs across 21 files [D: `grep -c "^type Bifrost.*struct" core/schemas/*.go`]).

## API contracts

Not an HTTP contract — see `data/api-contract_1.9.1_F-002.md`. The methods below are the actual "surface" this feature exposes: a 30-ish-method Go interface every provider must satisfy in full, with unimplemented operations returning a typed "not supported" error rather than omitting the method [D: core/schemas/provider.go:681-800; core/providers/groq/groq.go:88-90].

## Data model

Owns: every `Bifrost*Request`/`Bifrost*Response` struct family, `Key`, `ProviderConfig`, `NetworkConfig`, `BifrostError`, `ModelProvider`, `RequestType` [D: core/schemas/provider.go, core/schemas/bifrost.go, core/schemas/chatcompletions.go]. Reads/writes nothing external — schemas is pure data-shape + one interface, no I/O of its own. See `data/data-erd_1.9.1_F-002.md`.

## Sequence

Not a request-flow feature — schemas defines shapes and contracts that `core/bifrost.go`/`core/inference.go` (F-001) invoke against. The one behavioural sequence worth tracing is a context value write:

1. Caller invokes `ctx.SetValue(key, value)` on a `*BifrostContext` [D: core/schemas/context.go:475].
2. If `ctx` is plugin-scoped (`valueDelegate != nil`), the call recurses onto the root context — a scoped context never stores its own values [D: core/schemas/context.go:476-479].
3. If `blockRestrictedWrites` is set and `key` is one of the 25 reserved keys, the write is silently dropped — no error returned [D: core/schemas/context.go:480-484, core/schemas/context.go:19-45].
4. Otherwise the value lands in `userValues`, guarded by `valuesMu` [D: core/schemas/context.go:485-491].
5. A read (`Value(key)`) checks `userValues` first, then falls through to the parent context unless the parent is a pooled, non-cancelling `fasthttp.RequestCtx` (never read through — it may already be recycled) [D: core/schemas/context.go:387-413].

Plugin pipeline execution order (from the interface doc comment, `core/schemas/plugin.go:174-203`): `HTTPTransportPreAuthHook` → `HTTPTransportPreHook` → `PreRequestHook` → `PreLLMHook` → provider call → `PostLLMHook` (reverse registration order) → `HTTPTransportPostHook` (reverse) → `HTTPTransportStreamChunkHook` (reverse, per chunk, streaming only) [D: core/schemas/plugin.go:174-183].

## Failure modes

| Failure | Detection | Behaviour | Recovery |
| --- | --- | --- | --- |
| Plugin writes a reserved context key while `blockRestrictedWrites` is set | `isReservedKey(key)` returns true inside `SetValue`/`ClearValue`/`GetAndSetValue` | Write is silently dropped — no error, no log [D: core/schemas/context.go:480-484, 527-531, 547-551] | I: none visible in this package — basis: the write returns nothing and there is no log call on that path [D: core/schemas/context.go:481-484]. OPEN: should this path emit a debug log so a plugin author can discover a dropped write? |
| Provider does not implement an optional-interface method (`ResponsesLifecycleProvider`, `ResponsesNamespaceToolProvider`, `WebSocketCapableProvider`) | Type assertion (`provider.(ResponsesLifecycleProvider)`) fails at the call site outside this package | Falls back to a per-call "unsupported_operation" error or a per-provider default [D: core/schemas/provider.go:802-824 comments] | Caller sees a typed `*BifrostError`; no panic — the assertion is the guard |
| A required `Provider` method is simply unimplemented for a given provider | None inside schemas — the interface is structurally enforced by the Go compiler at each provider's own file | Provider file defines the method returning `providerUtils.NewUnsupportedOperationError(...)` [D: core/providers/groq/groq.go:88-90] | Caller receives a `*BifrostError`, not a compile error, because the interface itself has no optional methods — every provider must have *a* body for all 30+, even if it is one line |
| `NetworkConfig.RetryBackoffInitial`/`Max` given a bad duration string | `parseNetworkBackoffDuration` on unmarshal | Returns a wrapped error instead of a zero duration [D: core/schemas/bifrost.go is NOT the file — actually core/schemas/provider.go:154-175] | Caller's `json.Unmarshal` fails; no silent zero-backoff |

## Observability

No metrics, log events or trace-span emission calls live inside `core/schemas` itself — the package defines the `Tracer`/`Logger` interfaces (`trace.go`, `logger.go:1-79`) that other packages implement against, so it is a *contract* for observability, not a producer of it. `BifrostContext.SetTraceAttribute`/`Log`/`AppendRoutingEngineLog` (`core/schemas/context.go:809-931`) are the write paths a caller elsewhere in `core` uses.

- OPEN: is there a structured event-schema contract for observability anywhere in `core`, or is it ad hoc per caller?

## Traceability

Satisfies `F-002-US1`–`F-002-US3` (see `PRDs/prd_1.9.1_F-002-provider-abstraction.md`). No `DOM-nnn-R<k>` rules are promoted for this feature in `ddd/domain_DOM-001-core-engine.md` — the reserved-key guard and plugin pipeline symmetry are structural code behaviour, not business rules, so they are recorded here as failure modes instead. 

- OPEN: should the reserved-key silent-drop become a `DOM-001-R<k>` invariant? It is enforced in exactly one place (`core/schemas/context.go`) and tested (`context_test.go`), which is the domain-doc's own bar for promotion — flagged for the shared domain document owner to decide, not resolved here.
