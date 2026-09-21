---
title: PRD 1.9.1 F-003 — Provider Implementations
id: F-003
kind: prd
feature: F-003
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# PRD 1.9.1 F-003 — Provider Implementations

> Feature-level requirements: what and why, never how.

## Summary

Bifrost's core library talks to 30 third-party LLM/media provider APIs behind one common Go interface, so that a caller can switch or fall back between providers (Anthropic, OpenAI, Bedrock, Gemini, Groq, and 25 others) without changing its own request shape. I: this is the intent behind the package-per-provider structure — basis: every package implements the same `schemas.Provider` interface regardless of how different the upstream API is [D: core/schemas/provider.go:681-800; module layout, providers = 30 packages, 543 files].

## User stories

- **F-003-US1**: As a caller of Bifrost's core library, I want an OpenAI-wire-compatible provider (e.g. Groq) to behave identically to calling OpenAI directly, so that adding a new OpenAI-compatible backend costs almost no new code. I: inferred from Groq's `ChatCompletion` delegating entirely to `openai.HandleOpenAIChatCompletionRequest` with no Groq-specific transform — basis: [D: core/providers/groq/groq.go:101-116], evidenced by `GroqTests`-style suites existing per AGENTS.md's provider test convention.
- **F-003-US2**: As a caller, I want a provider with a genuinely different wire format (Anthropic, Bedrock) to still return Bifrost's own common response shape, so that my calling code never branches on which provider served the request. I: inferred from `ToBifrostChatResponse` existing symmetrically on every full-converter provider's response type — basis: [D: core/providers/anthropic/chat.go:1131; core/providers/bedrock/chat.go:91].
- **F-003-US3**: As a caller, I want provider-specific API quirks (Anthropic's document-block-needs-text rule, its adaptive-thinking model gating) handled transparently rather than surfaced as an upstream 400, so that my request doesn't need provider-specific pre-validation. I: inferred from the guard code sitting inside the converter, ahead of the HTTP call — basis: [D: core/providers/anthropic/chat.go:1052; core/providers/anthropic/adaptivethinkingstrip_test.go:182].

## Acceptance criteria

- F-003-US1: Given a chat completion request routed to a Groq model, when the request is sent, then it reaches Groq's `/v1/chat/completions` endpoint using OpenAI's own request/response converters, with no Groq-specific field mapping [D: core/providers/groq/groq.go:101-116].
- F-003-US2: Given a chat completion request routed to an Anthropic model, when Anthropic's response is parsed, then the caller receives a `*schemas.BifrostChatResponse` — the same type returned by every other provider [D: core/providers/anthropic/chat.go:1131,569].
- F-003-US3: Given a chat request containing a document content block with no text block, when it is converted for Anthropic, then a placeholder text block is inserted and the request is accepted by Anthropic rather than rejected [D: core/providers/anthropic/chat.go:1052].

## Implementation status

| Story | Status | Evidence |
| --- | --- | --- |
| F-003-US1 | wip — unverified, run `make test-core PROVIDER=groq` | F-003-TC1-class evidence exists; not executed this pass |
| F-003-US2 | wip — unverified, run `make test-core PROVIDER=anthropic` | F-003-TC1 |
| F-003-US3 | wip — unverified, run `make test-core PROVIDER=anthropic` | F-003-TC6 |

## Scope boundaries

Out of scope for F-003: the `Provider` interface's own shape (F-002), the routing/fallback logic that picks which provider handles a request (F-001), and MCP tool-calling (F-004). This feature is the providers/ package tree only.

## Dependencies

F-002 (Provider Abstraction) — every provider in this feature implements F-002's `Provider` interface and is constructed against F-002's `ProviderConfig`/`NetworkConfig` types.

## Metrics

OPEN: no success metric for "provider implementation quality" (e.g. parity coverage across providers, time-to-add-a-new-provider) is expressed anywhere in the code. AGENTS.md's "Adding a New Provider" checklist describes the *process* but not a target outcome.

## OPEN

OPEN: which providers are prioritized for new-feature parity (e.g. which non-chat operations — batch, containers, files — are expected on every full-converter provider vs. genuinely provider-specific)? Not recoverable — the "not supported" stub counts per provider (see `data/api-contract_1.9.1_F-003.md`) show the current state, not the target.
