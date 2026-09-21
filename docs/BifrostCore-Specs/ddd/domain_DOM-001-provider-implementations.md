---
title: Domain — Provider Implementations
id: DOM-001
kind: domain
feature: F-003
status: draft
owner: TBD
updated: 2026-09-21
---

# Domain — Provider Implementations

> Business rules, process and flow in the language of the business.

> Scope note: rule IDs here (`DOM-001-R<k>`) are local to this file, distinct from the hub-wide IDs in `domain_DOM-001-core-engine.md`. This file covers provider-specific wire-format quirks in `core/providers/`; cross-provider structural rules (the `Provider` interface contract itself) live in `domain_DOM-001-provider-abstraction.md`.

## Ubiquitous language

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| Full-converter provider | A provider package that owns its own request/response marshaling (anthropic, bedrock, gemini, vertex, cohere, …) [D: providers directory layout] | "native provider" |
| Delegator provider | A provider package whose upstream API is OpenAI-wire-compatible and re-uses `openai.HandleOpenAI*` functions directly (groq, cerebras, ollama, perplexity, openrouter, parasail, nebius, xai, sgl) [D: providers/groq/groq.go:101-116] | "thin provider" |
| Streaming client isolation | Each streaming request gets a client cloned via `providerUtils.BuildStreamingClient`, starting with empty reader/writer pools, so one non-idempotent stream-close can't poison another concurrent stream [D: providers/anthropic/anthropic.go:1514] | — |
| Wire type | A provider-specific request/response struct (e.g. `AnthropicMessageRequest`, `BedrockConverseResponse`) distinct from Bifrost's own `Bifrost*Request`/`Bifrost*Response` types [D: providers/anthropic/chat.go:339; providers/bedrock/chat.go:14] | "DTO" (not used in this codebase's own vocabulary) |

## Actors

- The engine (F-001) — calls each provider's `Provider` interface methods.
- The third-party provider API (Anthropic, Bedrock, Gemini, …) — the external system this feature converts to and from; entirely outside this repository.
- OPEN: which human decides the delegator/full-converter boundary for a new provider — not recorded in code (see architecture doc's own OPEN on this point).

## Business rules

1. **DOM-001-R1** — Anthropic rejects a message whose content contains a document block with no accompanying text block; the converter inserts a placeholder text block ahead of time so the request never reaches Anthropic in the invalid shape. [D: providers/anthropic/chat.go:1052]
2. **DOM-001-R2** — Anthropic's "adaptive" extended-thinking mode is rejected outright by legacy models (Opus 4.5/Haiku 4.5/Sonnet 4.5); Opus 4.6/Sonnet 4.6 accept both modes and `budget_tokens` still works. The sanitizer must not rewrite either case. [D: providers/anthropic/adaptivethinkingstrip_test.go:182]
3. **DOM-001-R3** — Every streaming request uses a client cloned fresh per request (dialer/TLS/proxy preserved, reader/writer pools empty), because a non-idempotent streaming-body close can otherwise poison fasthttp's shared reader pool across concurrent streams on the same provider. [D: providers/anthropic/anthropic.go:1514]
4. **DOM-001-R4** — A `Provider` method the target API cannot perform at all returns a one-line typed "not supported" `*BifrostError`, never a panic or a silently-missing method (e.g. Groq's `TextCompletion`/`Embedding`/`Rerank`/`OCR`, Anthropic's `Embedding`/`Speech`/`Transcription`). [D: providers/groq/groq.go:88,171,196,201; providers/anthropic/anthropic.go:2366,2371,2381]
5. **DOM-001-R5** — Extended-thinking (reasoning) token count is always a subset of output/completion tokens: `ReasoningTokens <= CompletionTokens`; no separate folding step enforces this because the provider's own usage accounting already guarantees it. [D: providers/anthropic/chat.go:1357]

## Process flow

D: full-converter unary chat path (Anthropic), cited in full in `architect/feature_1.9.1_F-003_architect.md`'s Sequence section:
1. `ChatCompletion` receives a `*schemas.BifrostChatRequest`.
2. `ToAnthropicChatRequest` converts it, inserting the placeholder text block if needed (R1) and validating the thinking-mode/model pairing (R2).
3. Sent over a per-request streaming or unary client (R3 applies to the streaming path only).
4. `response.ToBifrostChatResponse` converts the result back; a non-2xx becomes a `*schemas.BifrostError` via the shared error converter.

Delegator path (Groq and 8 others): step 2-4 above do not exist in the delegator's own package — `openai.HandleOpenAIChatCompletionRequest` performs them, parameterized by the delegator's base URL and client.

## Invariants

- `ReasoningTokens <= CompletionTokens` holds for every Anthropic response (R5).
- A document-only Anthropic message is never sent without an accompanying text block (R1).
- No two concurrent Anthropic streams ever share a live reader/writer pool (R3).

## Implementation status

| Rule | Status | Evidence |
| --- | --- | --- |
| DOM-001-R1 | wip — unverified, no dedicated test name surfaced beyond the code comment | `providers/anthropic/chat.go:1052` |
| DOM-001-R2 | wip — unverified, run `go test ./core/providers/anthropic/... -run TestAdaptiveThinkingStrip` | `providers/anthropic/adaptivethinkingstrip_test.go:182` |
| DOM-001-R3 | wip — unverified, no dedicated test name surfaced beyond the code comment | `providers/anthropic/anthropic.go:1514` |
| DOM-001-R4 | wip — unverified, run `go test ./core/providers/groq/...` and `./core/providers/anthropic/...` | `providers/groq/groq.go:88,171,196,201` |
| DOM-001-R5 | wip — unverified, no dedicated test name surfaced beyond the code comment | `providers/anthropic/chat.go:1357` |

None run in this session — `core/`'s provider tests hit live third-party APIs per AGENTS.md; not run unattended.

## Open questions

- OPEN: why is the delegator/full-converter split drawn where it is for borderline providers (e.g. why does a given provider get its own package instead of delegating, if its API is largely OpenAI-shaped)? Not recoverable from code.
- OPEN: is R1/R3/R5 tested by name anywhere, or only asserted in a code comment next to the enforcing line? If untested, this is a real coverage gap, not just a documentation gap.
- OPEN: is there a capability matrix (e.g. `modelcaps.go`, not surveyed in this pass) that declares which providers implement which subset of the 30+ interface methods, rather than requiring a manual read of each package?
