---
title: Master Architecture — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Master Architecture — BifrostCore

> System-level architecture: components, data, integration points and the ADRs behind them.

## System context

D: `core/` has no external actor of its own — no HTTP surface, no entrypoint [D: survey "HTTP surface: none found", "Entrypoints: none found"]. It crosses two kinds of boundary: (1) outbound, to 20+ LLM/voice/image provider APIs over `fasthttp`/`net-http` [D: core/network/http.go:449]; (2) inbound, as a Go library called by `transports/bifrost-http` and `cli/`, which are separate modules [D: go.work:1; repowise architecture map edge `module_transports_bifrost_http_handlers -> module_core_providers` (120 refs)].

## Component view

| Component | Responsibility | Owns which data | Talks to whom |
| --- | --- | --- | --- |
| F-001 Core Engine (`bifrost.go`, `inference.go`, `network/`) | Request queuing, routing, fallback/retry, key rotation | `ChannelMessage`, `Fallback`, `BifrostRequest`/`BifrostResponse` in flight [D: core/schemas/bifrost.go:571,553,1125] | Provider implementations (F-003), via the `Provider` interface (F-002) |
| F-002 Provider Abstraction (`schemas/`) | Defines the `Provider` interface (30+ methods), `BifrostContext`, plugin interfaces, all wire types | The type contract itself — no runtime state | Everything else in `core/` imports it; imports nothing back [D: repowise edges — `providers -> types` 5,740 refs, `internal -> types` 4,130 refs, no reverse edge reported] |
| F-003 Provider Implementations (`providers/`) | 20+ per-provider converters + HTTP orchestration | Nothing persisted — pure request/response transforms plus one live HTTP call each | The external provider's API; implements F-002's `Provider` interface |
| F-004 MCP Integration (`mcp/`) | Agent orchestration loop, tool/client lifecycle, Starlark codemode sandbox | `MCP client` connection state (`Disconnected`/`Connected`) [D: core/mcp/clientmanager.go:2090] | MCP tool servers (external); F-001's request path when tool_choice is present |
| `core/pool/` (cross-cutting, not its own feature) | Generic `Pool[T]`, dual prod/debug build | Pooled object lifecycles | All four features that pool objects |
| `core/internal/` (test infra, not a shipped component) | `llmtests` (live-API scenario tests), `mcptests` (mock-based) | Test fixtures/mocks | Exercises F-001–F-004 |

## Data architecture

`core/` owns no persistent store — it is a stateless library (confirmed by the survey finding a single low-confidence, unextractable entity and zero DB/ORM signal [D: survey "Entities" — `providers/gemini/types.go:1345`, confidence: low]). See `data/data-master-erd.md` for the type-contract registry this reversal derived instead of a persistence model — do not restate it here.

## API surface

`core/` publishes no HTTP/topic surface (`survey "HTTP surface: none found"`). Its surface is the Go `Provider` interface — 30+ methods (`ChatCompletion`, `ChatCompletionStream`, `Responses`, `Embedding`, `Speech`, `ImageGeneration`, `Batch*`, `File*`, `Container*`, …) [D: core/schemas/provider.go:681]. See each feature's `data/api-contract_1.9.1_F-*.md` for the per-feature method-level detail.

## Cross-cutting concerns

- Config/context: `BifrostContext`, a custom mutable `context.Context` — see `architect_common.md`'s naming/layout section and `core/schemas/context.go:77`.
- Error handling: `BifrostError`/`BifrostErrorExtraFields` carry provider/model/request-type metadata on every error [D: core/schemas/bifrost.go:1954,2108].
- Pooling: see `architect_common.md` Design patterns.
- OPEN: tracing/observability wiring specifics beyond the `Tracer` interface named in AGENTS.md (not independently re-derived from a `core/`-scoped citation in this pass).

## Decision index

| ADR ID | Decision | Affected components |
| --- | --- | --- |
| ADR-0001 | Bootstrap: architecture decisions for this hub are recorded as ADRs from this point forward | All |

No other ADR exists in this reversed hub. I: several architecturally significant choices are visible in code with no recorded rationale (e.g. the dual fasthttp-unary/streaming-client-per-request pattern, `providers/anthropic/anthropic.go:1514`) — per `filling.md`, these are candidates for a reconstructed ADR with an honest `OPEN:` on rationale, not written here to keep this pass scoped; OPEN: should one be authored per such pattern.

## Feature architecture index

| Version | Feature ID | Link |
| --- | --- | --- |
| 1.9.1 | F-001 | `architect/feature_1.9.1_F-001_architect.md` |
| 1.9.1 | F-002 | `architect/feature_1.9.1_F-002_architect.md` |
| 1.9.1 | F-003 | `architect/feature_1.9.1_F-003_architect.md` |
| 1.9.1 | F-004 | `architect/feature_1.9.1_F-004_architect.md` |
