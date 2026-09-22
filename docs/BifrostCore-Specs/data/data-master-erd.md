---
title: Master Data Model & ERD — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Master Data Model & ERD — BifrostCore

> The system-wide entity registry and relationship map. Every entity is introduced here once and referenced everywhere else.

> This registry is a **Go type contract**, not a persistence schema. The survey found no DDL, migration or ORM model scoped to `core/` — one low-confidence, unextractable struct was flagged as noise [D: survey "Entities" — `core/providers/gemini/types.go:1345`, confidence: low]. `core/` is stateless: it defines the shapes that flow through it in memory and over the wire to providers, and persists nothing itself. Actual storage lives in `framework/configstore` and `framework/logstore`, outside this reversed scope — OPEN whether those should get their own future reversal pass.

## Entity registry

| Entity (`schemas.json` $defs key) | Owning component | Introduced by feature | System of record | Retention |
| --- | --- | --- | --- | --- |
| `ChannelMessage` | F-001 | F-001 | In-memory only, pooled (`core/pool/`) | Released back to pool at request end [D: core/bifrost.go:62] |
| `Fallback` | F-001 | F-001 | Config (`BifrostConfig`), in-memory | Lifetime of the `Bifrost` instance [D: core/schemas/bifrost.go:553] |
| `BifrostContext` | F-002 | F-002 | In-memory, per-request | Request lifetime [D: core/schemas/context.go:77] |
| `Provider` (interface, not a data entity but the contract every provider type satisfies) | F-002 | F-002 | N/A — behavioural contract | N/A [D: core/schemas/provider.go:681] |
| `NetworkConfig` / `ProviderConfig` | F-002 | F-002 | Config, in-memory | Lifetime of the `Bifrost` instance [D: core/schemas/provider.go:60,556] |
| `PluginConfig` / `HTTPRequest` / `HTTPResponse` | F-002 | F-002 | Pooled, in-memory | Released via Acquire/Release pattern [D: core/schemas/plugin.go:401,42,93] |
| `BifrostRequest` / `BifrostResponse` / `BifrostStreamChunk` | F-001/F-002 boundary | F-001 | In-memory, per-request/per-chunk | Request or stream lifetime [D: core/schemas/bifrost.go:571,1125,1913] |
| `BifrostError` / `BifrostErrorExtraFields` | F-002 | F-002 | In-memory | Request lifetime [D: core/schemas/bifrost.go:1954,2108] |
| `BifrostChatRequest` / `BifrostChatResponse` / `ChatMessage` / `ChatTool` | F-002 (shape) / F-003 (per-provider conversion) | F-002 | In-memory | Request lifetime [D: core/schemas/chatcompletions.go:14,36,1100,418] |
| `BifrostLLMUsage` / `BifrostCost` | F-002 | F-002 | In-memory | Attached to response, request lifetime [D: core/schemas/chatcompletions.go:1925,2050] |
| MCP client connection entry (`Disconnected`/`Connected` state) | F-004 | F-004 | In-memory (`core/mcp/clientmanager.go`) | Lifetime of the MCP client registration [D: core/mcp/clientmanager.go:2090] |

I: every provider-specific type (e.g. `AnthropicChatRequest`, if it exists under that exact name) is a per-feature (F-003) *conversion target* of the F-002 entities above, not a separate registry entry — basis: AGENTS.md's stated converter-function naming convention (`To<Provider><Feature>Request`) implies a shape-preserving transform, not a new canonical entity. OPEN: confirm no provider-specific type carries state the canonical `Chat*` types don't.

## Master ERD

See `schema/erd_master.puml`. The diagram cannot show *why* `BifrostContext` sits outside the request/response entities rather than embedded in them: I: this is deliberate isolation — basis — AGENTS.md's own hard rule ("never store stream-sized data in BifrostContext... route storage through a manager, keep only the ID in ctx"), which this reversal did not independently re-verify against `context.go`'s current field list in this pass.

## Relationships and cardinality

| From | To | Cardinality | Ownership (who may delete) | Referential rule |
| --- | --- | --- | --- | --- |
| `ChannelMessage` | `BifrostRequest` | 1:1 (embeds/references) | F-001's pool release path | Cleared, not deleted (pooled) [D: core/bifrost_test.go:3555 — release must clear all references] |
| `BifrostRequest` | `Fallback` | 1:N (a request may configure several fallbacks) | Config owner | N/A — config, not a live reference |
| `BifrostContext` | governance/trace/retry keys | 1:N (key-value) | Whichever plugin/internal code set the reserved key | Write-once via `BlockRestrictedWrites()` for reserved keys [I: basis — AGENTS.md's stated gotcha #11, not independently re-derived from `context.go` line evidence in this pass] |

OPEN: cardinality between `Provider` implementations and `ProviderConfig` — one config per provider instance, or shared — not independently verified in this pass.

## Identity and keys

- D: no entity here carries a database surrogate key (uuid/serial) — all are in-memory Go values scoped to a request or a pool slot.
- D: `BifrostContextKey` is a typed string key (e.g. `"x-bf-vk"`, `"request-id"`) [D: core/schemas/bifrost.go:240,244] — the closest thing to an "ID format" in this registry, and it is a constant set, not a generated identifier.
- OPEN: whether `RequestID` (`BifrostContextKeyRequestID`) is guaranteed globally unique or only per-process — not stated in the cited evidence.

## Consistency rules

- DOM-001-R9 (`ReasoningTokens <= CompletionTokens`) is a cross-field invariant on `BifrostLLMUsage`/`ChatCompletionTokensDetails` [D: core/schemas/chatcompletions.go:1925,2030; rule cited in `ddd/domain_DOM-001-core-engine.md`].
- DOM-001-R10 (`ChannelMessage` exclusive claim) is a cross-time invariant, not a cross-field one — see the domain doc.
- OPEN: no `not null`/`unique`/`check`-equivalent constraint exists to inspect (no DB), so most Go-level invariants (nil-safety, required fields) were not exhaustively enumerated in this pass — this is a genuine coverage gap, not a claim that none exist.

## Change policy

OPEN: `core/` has no migration mechanism (it's not a database) — how a breaking type change here is coordinated with `transports/`, `cli/` and the plugin modules that import it is described only in AGENTS.md's "Provider Interface Has 30+ Methods" gotcha (a 6-step change checklist), not independently re-verified against `core/`'s own commit history in this pass. OPEN: is there a deprecation window before a `Provider` interface method's signature can change.

## Open questions

- OPEN: is the "type contract, not persistence schema" framing correct, or does `core/` genuinely have some entity this survey mis-scored as low-confidence noise (`core/providers/gemini/types.go:1345`)? Worth a manual read before treating this registry as complete.
- OPEN: should `framework/configstore`'s actual persisted entities be cross-referenced here as "consumers of core's contract," given `core/` defines the shapes but never stores them?
