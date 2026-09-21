---
title: Domain — Provider Abstraction
id: DOM-001
kind: domain
feature: F-002
status: draft
owner: TBD
updated: 2026-09-21
---

# Domain — Provider Abstraction

> Business rules, process and flow in the language of the business.

> Scope note: rule IDs here (`DOM-001-R<k>`) are local to this file, distinct from the hub-wide `DOM-001-R<k>` IDs in `domain_DOM-001-core-engine.md`. This file covers only the type-contract layer (`core/schemas/`); see the core-engine domain doc for the request-lifecycle rules that build on top of it.

## Ubiquitous language

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| Provider interface | The 30+ method Go interface every LLM/media backend implements [D: core/schemas/provider.go:681-800] | "adapter interface" |
| BifrostContext | Thread-safe mutable `context.Context` carrying request-scoped values via `SetValue`/`WithValue` [D: core/schemas/context.go:77-94] | "ctx" (fine in code, not in domain prose) |
| Reserved key | A `BifrostContextKey` internal systems write (governance, retry, fallback, trace) that plugin code must never write directly [D: core/schemas/context.go:19-45] | "system key" |
| Plugin hook | One of `PreLLMHook`/`PostLLMHook`/`PreMCPHook`/`PostMCPHook`/HTTP-transport hooks/`Inject` [D: core/schemas/plugin.go:213-477] | "middleware" (reserved for HTTP-layer usage elsewhere) |
| Not-supported operation | A `Provider` method a given implementation cannot perform, returning a typed `*BifrostError` rather than omitting the method [D: core/providers/groq/groq.go:88-90] | "unimplemented" (implies missing, not a typed refusal) |

## Actors

- The engine (F-001, `core/bifrost.go`/`core/inference.go`) — the sole caller of `Provider` interface methods and the only writer permitted to reserved `BifrostContext` keys.
- A plugin author — writes `LLMPlugin`/`MCPPlugin`/`HTTPTransportPlugin`/`ObservabilityPlugin` implementations against these interfaces; their writes to reserved keys are silently dropped, never erred.
- A provider implementer (F-003) — must satisfy every method on `Provider`, returning a typed refusal for anything genuinely unsupported.
- OPEN: whether an external SDK consumer (outside `transports/`) is expected to hold a `*BifrostContext` directly, or always receives one already constructed by the engine — not stated in `core/schemas`.

## Business rules

1. **DOM-001-R1** — A write to a reserved `BifrostContext` key is silently dropped when `blockRestrictedWrites` is set: no error is returned, no log is emitted on that path. [D: core/schemas/context.go:480-484]
2. **DOM-001-R2** — A scoped (plugin-local) `BifrostContext` never stores its own values; every `SetValue` call recurses to the root context. [D: core/schemas/context.go:476-479]
3. **DOM-001-R3** — Every `Provider` implementation must define a body for all 30+ interface methods; a method the target API cannot perform returns a typed `*BifrostError` ("not supported"), never a missing method or a panic. [D: core/schemas/provider.go:681-800; core/providers/groq/groq.go:88-90]
4. **DOM-001-R4** — Plugin hooks execute in a LIFO wrapping order: pre-hooks in registration order, post-hooks in reverse registration order, guaranteeing every executed pre-hook's matching post-hook also runs. [D: core/schemas/plugin.go:174-203]

## Process flow

D: a context value write (see `architect/feature_1.9.1_F-002_architect.md`'s Sequence section for the full cited call chain) — restated here only as the domain-level shape:
1. Caller (plugin or engine) calls `SetValue`.
2. Scoped context → recurse to root (R2).
3. Reserved key + guard active → drop silently (R1).
4. Otherwise → store under `userValues`.

## Invariants

- A `Provider` implementation always has 30+ methods with bodies — the Go compiler enforces this structurally, so violation is impossible at compile time (R3).
- A reserved key's value, once set by the engine, cannot be overwritten by plugin code while the guard is active (R1).

## Implementation status

| Rule | Status | Evidence |
| --- | --- | --- |
| DOM-001-R1 | wip — unverified, run `go test ./core/schemas/... -run TestBlockRestrictedWrites` (exact test name not confirmed by survey; a `context_test.go` exists per the F-002 fork's pass) | `core/schemas/context.go:480-484` |
| DOM-001-R2 | wip — unverified, no dedicated test name surfaced in survey | `core/schemas/context.go:476-479` |
| DOM-001-R3 | wip — unverified, run `go test ./core/providers/groq/...` | `core/providers/groq/groq.go:88-90` (one example provider) |
| DOM-001-R4 | wip — unverified, no dedicated test name surfaced in survey for pipeline LIFO ordering specifically | `core/schemas/plugin.go:174-203` (doc comment, not a test) |

None run in this session — `core/`'s test suite includes live-provider-API cases; not run unattended (see `tests/testing_strategy.md`).

## Open questions

- OPEN: should the reserved-key silent-drop (R1) log at debug level so a plugin author can discover a dropped write, instead of failing silently? Flagged by the F-002 architecture doc; not decided here.
- OPEN: is R4 (plugin LIFO ordering) tested anywhere as a named case, or only asserted in the interface doc comment? Not found in this survey pass.
- OPEN: which human role (platform engineer vs. application developer) is the intended plugin author — not stated in code.
