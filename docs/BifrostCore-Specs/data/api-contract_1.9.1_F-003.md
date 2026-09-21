---
title: API Contract 1.9.1 F-003 — Provider Implementations
id: F-003
status: draft
owner: TBD
updated: 2026-09-21
---

# API Contract 1.9.1 F-003 — Provider Implementations

> The wire contract for this feature — the readable companion to its OpenAPI and AsyncAPI files.

## Surface summary

`core/providers/` exposes no inbound HTTP endpoints — [D: reverse.py survey, root=core/, "HTTP surface: none found"]. It is a library consumed in-process by the core engine (F-001); the only externally reachable contract is **outbound**, against each third-party provider's own API (Anthropic's `api.anthropic.com`, OpenAI's `api.openai.com`, AWS Bedrock, etc.), which are not in this repository and are `OPEN` by definition. `schema/openapi_1.9.1_F-003.json` and `schema/asyncapi_1.9.1_F-003.json` are therefore left as their generated stubs (`paths: {}`) — there is no inbound contract to fill them with.

The contract this document can actually state is the **Go interface contract**: which of the `schemas.Provider` interface's 51 methods [D: core/schemas/provider.go:681-800] a given provider package implements versus stubs out as unsupported.

## Endpoints

None (inbound). N/A.

## Events

None found — [D: reverse.py survey, core/, events section lists only unused declared message-type constants unrelated to this feature, e.g. `schemas/mcp.go:56`, `schemas/oauth.go:119,124`, none referenced from `core/providers/`].

## Error model

Every provider funnels its parsed HTTP error through `providerUtils.HandleProviderAPIError(resp, errorResp)` into one shared `*schemas.BifrostError` shape [D: core/providers/utils/utils.go:2128], then a provider-specific parser adds provider fields on top, e.g. `ParseAnthropicError` [D: core/providers/anthropic/errors.go:61]. Per AGENTS.md, `bifrostErr.ExtraFields.Provider`/`ModelRequested`/`RequestType` are always set — this document does not re-derive that beyond citing it, since it is common to every provider and belongs in `architect_common.md`.

## Versioning and compatibility

OPEN: no version-negotiation or deprecation-window logic was found scoped to `core/providers/` itself in this pass — providers are added/removed at the Go-module level (AGENTS.md's "Adding a New Provider" checklist), not versioned individually. Whether an individual provider's converter logic carries its own compatibility window (e.g. for a provider API version bump) is not decidable without reading every provider's `utils.go` for version constants, which this pass did not do exhaustively.

## Spec files

- `schema/openapi_1.9.1_F-003.json` — intentionally empty `paths: {}`; no inbound endpoints.
- `schema/asyncapi_1.9.1_F-003.json` — intentionally empty; no inbound events.
- The **real** contract surface for this feature is `core/schemas/provider.go:681-800` (the `Provider` interface) plus, per package, the "not supported" stub count — sampled here rather than tabulated for all 30 packages: Groq implements ~10 of 51 methods and stubs the remaining ~41 as "not supported" [D: core/providers/groq/groq.go, grep count of "not supported" comment lines: 41; e.g. `TextCompletion` at groq.go:88, `Embedding` at groq.go:171]; Anthropic implements substantially more (chat, responses, batch, files, containers, images) and stubs a narrower set — embedding, speech, transcription [D: core/providers/anthropic/anthropic.go:2366,2371,2381].

## Traceability

`F-003-US*` in `PRDs/prd_1.9.1_F-003-provider-implementations.md`.

## OPEN

OPEN: is "which interface methods a provider implements" tracked anywhere as a queryable capability matrix (for the UI/config layer to know what a provider can do), or does every caller have to try the call and handle the "not supported" error at runtime? Not visible from `core/providers/` alone — AGENTS.md's `core/schemas/modelcaps.go` (outside this feature's scope) may be the answer, but that file was not surveyed here.
