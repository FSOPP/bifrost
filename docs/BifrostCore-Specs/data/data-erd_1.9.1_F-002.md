---
title: Data Model 1.9.1 F-002 — Provider Abstraction
id: F-002
status: draft
owner: TBD
updated: 2026-09-21
---

# Data Model 1.9.1 F-002 — Provider Abstraction

> The slice of the data model this feature reads and writes, at field precision.

## Scope

I: these are Go in-memory type definitions, not persisted database entities — basis: `core/schemas` has no DB driver import, no ORM tag beyond `json:`, and the survey's own entity extractor found only one low-confidence, unrelated hit (`providers/gemini/types.go:1345`, fields not extractable) [D: survey.md "Entities"]. "Own" below means "defines the Go struct"; core/schemas performs no I/O of its own.

- **Own**: `Provider` interface (core/schemas/provider.go:681), `BifrostContext` (core/schemas/context.go:77), `Key` (core/schemas/account.go:135), `ProviderConfig`/`NetworkConfig`/`CustomProviderConfig`/`AllowedRequests` (core/schemas/provider.go:53-676), `BifrostError`/`BifrostErrorExtraFields` (core/schemas/bifrost.go:1954, 2108), `ModelProvider`/`RequestType` enums (core/schemas/bifrost.go:43, 128), one `Bifrost*Request`/`Bifrost*Response` pair per operation family — chat (core/schemas/chatcompletions.go), responses (responses.go), embedding (embedding.go), images (images.go), batch (batch.go), files (files.go), videos (videos.go), containers (containers.go), cached contents (cachedcontents.go), speech (speech.go), transcriptions (transcriptions.go), passthrough (passthrough.go) — 129 top-level `Bifrost*` structs total across 21 files [D: `grep -c "^type Bifrost.*struct" core/schemas/*.go`].
- **Read/write**: nothing external — no store client lives in this package.
- Out of bounds: provider-specific wire types (`AnthropicChatRequest` etc., owned by F-003), the MCP protocol types in `schemas/mcp.go` (owned by F-004's boundary even though the file lives in `schemas/` — cross-referenced, not duplicated here).

## Feature ERD

See `schema/erd_1.9.1_F-002.puml` — covers the 5 most central entities only (`Provider` interface, `BifrostContext`, `Key`, `BifrostChatRequest`/`BifrostChatResponse`, `BifrostError`). 

OPEN: the full 129-struct inventory is not diagrammed — see scope note in Field definitions.

## Field definitions

I: full field-by-field tables for all 129 `Bifrost*` structs across 14,443 lines of `core/schemas/*.go` exceed this document's practical scope — basis: the four families below were selected as the entities every provider and the engine actually depend on (per repowise's PageRank-ranked "most central files": `core/schemas/bifrost.go`, `core/schemas/chatcompletions.go`, `core/schemas/context.go`, `responses.go`). The remaining families (batch, files, videos, containers, cached contents, speech, transcriptions, passthrough, images) follow the identical `Bifrost<Op>Request`/`Bifrost<Op>Response` pattern and are left as a gap rather than transcribed at low value.

OPEN: should the remaining 9 operation families (batch, files, videos, containers, cached contents, speech, transcriptions, passthrough, images) get their own field-by-field inventory in a future pass?

**`BifrostChatRequest`** [D: core/schemas/chatcompletions.go:14-21]

| Field | Type | Nullable | Notes |
| --- | --- | --- | --- |
| Provider | ModelProvider | no | |
| Model | String | no | |
| Input | []ChatMessage | yes (`omitempty`) | |
| Params | *ChatParameters | Yes | |
| Fallbacks | []Fallback | Yes | |
| RawRequestBody | []byte | n/a (`json:"-"`) | used only when `BifrostContextKeyUseRawRequestBody` is set [D: core/schemas/chatcompletions.go:20; AGENTS.md context-keys table] |

**`BifrostChatResponse`** [D: core/schemas/chatcompletions.go:36-55] — `ID`, `Choices []BifrostResponseChoice`, `Created int` (unix seconds), `Model string`, `Object string`, `ServiceTier *BifrostServiceTier`, `Speed *string` ("fast"/"standard" — Anthropic fast-mode billing), `InferenceGeo *string` ("us"/"global" — Anthropic data-residency 1.1x multiplier), `Diagnostics *CacheDiagnostics`, `SystemFingerprint string`, `Usage *BifrostLLMUsage`, `ExtraFields BifrostResponseExtraFields`, plus Perplexity-specific `SearchResults`/`Videos`/`Citations`.

**`Key`** [D: core/schemas/account.go:135-160, 19 fields] — `ID`, `Name`, `Value SecretVar`, `Models WhiteList`, `BlacklistedModels BlackList`, `Weight float64` (load-balancing), `Aliases KeyAliases`, seven `*<Provider>KeyConfig` pointer fields (Azure/Vertex/Bedrock/BedrockMantle/VLLM/Replicate/Ollama/SGL/Databricks/GithubCopilot), `Enabled *bool`, `UseForBatchAPI *bool` (I: defaults differ by key age — basis: comment states "default:false for new keys, migrated keys default to true" [D: core/schemas/account.go field comment]), `UseAnthropicEndpoints`/`UseOpenAIEndpoints *bool`, `ConfigHash string`, `Status KeyStatusType`, `Description string`.

**`BifrostError`** [D: core/schemas/bifrost.go:1954-1963] — see `api-contract_1.9.1_F-002.md` Error model section; not duplicated here.

**`NetworkConfig`** [D: core/schemas/provider.go:60-77] — `BaseURL`, `ExtraHeaders map[string]string` (deep-copied on `CheckAndSetDefaults` to prevent data races — AGENTS.md gotcha #4, verified at core/schemas/provider.go:663-667), `DefaultRequestTimeoutInSeconds`, `MaxRetries`, `RetryBackoffInitial`/`Max time.Duration` (JSON: duration string or legacy int-milliseconds, `UnmarshalJSON` at core/schemas/provider.go:85-148), `InsecureSkipVerify`, `CACertPEM *SecretVar`, `StreamIdleTimeoutInSeconds`, `KeepAliveTimeoutInSeconds`, `MaxConnsPerHost` (clamped to `MaxConnsPerHostUpperBound=10000` in `CheckAndSetDefaults`, core/schemas/provider.go:651-655), `EnforceHTTP2`, `HTTP2PingIntervalInSeconds` (clamped to 3600s to avoid an int64 overflow in the Bedrock transport's `* time.Second` conversion — core/schemas/provider.go:26-31, :657-661), `BetaHeaderOverrides map[string]bool`, `AllowPrivateNetwork bool`.

## New and changed entities

This is the seed feature for the shared data model — `data-master-erd.md`'s entity registry rows for `Provider`, `BifrostContext`, `Key`, `BifrostChatRequest`/`Response`, `BifrostError`, `NetworkConfig`/`ProviderConfig` are proposed by this document. **Coordination note**: `data-master-erd.md` and `schema/schemas.json` are shared, product-level files outside this document's write scope (owned by the hub-level pass) — the entities above should be reflected there as `$defs` entries with `"Introduced by": "F-002"`; not written here to avoid a concurrent-edit conflict with the shared-docs pass.

## Migrations

None. No database, no migration directory in `core/schemas` — these are compile-time Go type definitions.

## Traceability

`F-002-US1`, `F-002-US2` (see PRD). No `DOM-nnn-R<k>` rules cited yet — pending the shared domain document.
