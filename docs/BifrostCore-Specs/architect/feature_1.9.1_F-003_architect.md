---
title: Feature Architecture 1.9.1 F-003 — Provider Implementations
id: F-003
kind: architecture
feature: F-003
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Feature Architecture 1.9.1 F-003 — Provider Implementations

> Low-level design for one feature: contracts, schema, sequence, failure modes.

## Design summary

`core/providers/` holds one Go package per third-party LLM/media API (30 directories) [D: core/providers (module layout)]. Each package implements the `schemas.Provider` interface (`core/schemas/provider.go:681-800`) and falls into one of two shapes: a **full converter** that owns its own request/response marshaling (anthropic, bedrock, gemini, vertex, cohere, …), or a **thin delegator** that re-uses the OpenAI package's converters and HTTP orchestration because the upstream API is itself OpenAI-wire-compatible (groq, cerebras, ollama, perplexity, openrouter, parasail, nebius, xai, sgl — `core/providers/groq/groq.go:101-116` calls `openai.HandleOpenAIChatCompletionRequest` directly for `ChatCompletion`). I: This package-per-provider layout keeps one provider's outage or quirk from requiring a change to any other provider's code — basis: no shared mutable state between provider packages, and each holds its own `client`/`streamingClient` fasthttp.Client pair [D: core/providers/groq/groq.go:30-51].

## API contracts

See `data/api-contract_1.9.1_F-003.md`. In short: this feature has no inbound HTTP surface of its own (0 endpoints found in core/providers — [D: reverse.py survey, core/, HTTP surface: none found]); its contract is outbound, against each third-party provider's API, and Go-side it is "which of the 51 `Provider` interface methods does this package actually implement."

## Data model

See `data/data-erd_1.9.1_F-003.md`. This feature owns no persisted entity; it transforms in-memory Go structs (Bifrost's own request/response types, owned by F-002, into provider-specific wire structs it defines itself, e.g. `AnthropicMessageRequest`/`AnthropicMessageResponse` [D: core/providers/anthropic/chat.go:339,1131], `BedrockConverseRequest`/`BedrockConverseResponse` [D: core/providers/bedrock/chat.go:14,91]).

## Sequence

Unary chat completion, full-converter path (Anthropic) [D: core/providers/anthropic/chat.go:493-569]:
1. `AnthropicProvider.ChatCompletion` receives a `*schemas.BifrostChatRequest`.
2. `ToAnthropicChatRequest(ctx, bifrostReq)` converts it to `*AnthropicMessageRequest` [D: core/providers/anthropic/chat.go:339].
3. The request is sent over `provider.client` (unary fasthttp client).
4. On success, `response.ToBifrostChatResponse(ctx)` — a method on the parsed `*AnthropicMessageResponse`, not a free function — converts back to `*schemas.BifrostChatResponse` [D: core/providers/anthropic/chat.go:1131,569].
5. On a non-2xx response, `ParseAnthropicError(resp)` builds a `*schemas.BifrostError` [D: core/providers/anthropic/errors.go:61], itself built on the shared `providerUtils.HandleProviderAPIError` [D: core/providers/utils/utils.go:2128].

Unary chat completion, delegator path (Groq) [D: core/providers/groq/groq.go:101-116]:
1. `GroqProvider.ChatCompletion` calls `openai.HandleOpenAIChatCompletionRequest` with Groq's own base URL and `provider.client`, and returns whatever that shared function returns — no Groq-specific conversion code exists in this path.

I: `ToBifrost<Feature>Response` is documented in AGENTS.md as a plain function, but in both Anthropic and Bedrock it is implemented as a method on the provider's own response type (`(response *AnthropicMessageResponse) ToBifrostChatResponse(...)`, `(response *BedrockConverseResponse) ToBifrostChatResponse(...)`) — basis: grep across both packages found zero free-function matches for that name and two method-receiver matches [D: core/providers/anthropic/chat.go:1131; core/providers/bedrock/chat.go:91]. Convention as documented and convention as practiced diverge on receiver style, not on direction or naming.

## Failure modes

| Failure | Detection | Behaviour | Recovery |
| --- | --- | --- | --- |
| Anthropic rejects a document content block with no sibling text block | Anthropic returns a 400 `invalid_request_error` naming the missing text block | `ToAnthropicChatRequest` inserts a placeholder text block ahead of time so the request never reaches Anthropic in the invalid shape [D: core/providers/anthropic/chat.go:1052] | n/a — prevented before send |
| A provider's streaming body-close is non-idempotent and can poison fasthttp's shared reader pool across concurrent streams | n/a — structural | Each streaming request gets a client cloned via `providerUtils.BuildStreamingClient`, preserving dialer/TLS/proxy but starting with empty reader/writer pools [D: core/providers/anthropic/anthropic.go:1514; core/providers/groq/groq.go:51] | n/a — isolated per request |
| Anthropic model doesn't support the requested "adaptive" thinking mode | Model-ID gate in the request sanitizer | Legacy models (Opus/Haiku/Sonnet 4.5) have `"adaptive"` rejected outright; Opus/Sonnet 4.6 accept both modes and `budget_tokens` — the sanitizer must not rewrite either case [D: core/providers/anthropic/adaptivethinkingstrip_test.go:182] | n/a — validated before send |
| A method the target provider's API cannot do at all | Compile-time: the interface requires it | Method body is a one-line "not supported" stub returning a `*schemas.BifrostError`, e.g. Groq's `TextCompletion`/`Embedding`/`Rerank`/`OCR` [D: core/providers/groq/groq.go:88,171,196,201] or Anthropic's `Embedding`/`Speech`/`Transcription` [D: core/providers/anthropic/anthropic.go:2366,2371,2381] | Caller sees a structured "not supported" error, never a panic or silent no-op |

## Observability

No metrics, log, or trace-span emission was found inside `core/providers/` itself in this survey pass — [D: reverse.py survey, core/, "telemetry libraries: none found"]. OPEN: does the caller (core engine / plugin pipeline) instrument provider calls from the outside, or is provider-level latency/error observability genuinely absent at this layer? Not decidable from `core/providers/` alone; the `Tracer` interface referenced in AGENTS.md's context section lives in `core/schemas`, outside this feature's files.

## Traceability

Satisfies `F-003-US*` in `PRDs/prd_1.9.1_F-003-provider-implementations.md`; enforces no `DOM-nnn` rule of its own (see `ddd/domain_DOM-001-core-engine.md`, owned by another feature) since core/providers/ was not the module surveyed for domain constraints in this pass.

## OPEN

OPEN: why is the delegator/full-converter split drawn where it is (i.e., why does Databricks get its own package instead of delegating, if its API is also largely OpenAI-shaped)? Not recoverable from the code — the split tracks upstream API compatibility, but the boundary decision for borderline providers isn't recorded anywhere in `core/providers/`.
