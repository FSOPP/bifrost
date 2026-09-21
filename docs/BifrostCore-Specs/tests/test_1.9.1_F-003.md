---
title: Test Plan 1.9.1 F-003 — Provider Implementations
id: F-003
kind: test
feature: F-003
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Test Plan 1.9.1 F-003 — Provider Implementations

> Concrete cases traced back to acceptance criteria.

## Traceability matrix

| Story/AC | Test case(s) | Level |
| --- | --- | --- |
| F-003-US1 (delegator providers reuse OpenAI wire format) | F-003-TC1, F-003-TC2 | unit |
| F-003-US2 (full-converter providers produce correct native wire shapes) | F-003-TC3, F-003-TC4, F-003-TC5 | unit |
| F-003-US3 (per-provider quirks are guarded explicitly) | F-003-TC6, F-003-TC7 | unit |

## Test cases

- **F-003-TC1** — `AnthropicTests` top-level suite entry [D: core/providers/anthropic/anthropic_test.go:82]. Preconditions: none stated beyond package setup. Steps/expected: table-driven, not expanded in this pass.
- **F-003-TC2** — `AzureTests` [D: core/providers/azure/azure_test.go:108]; `AliasModelNameResolvesTheDatasheetRow` [D: core/providers/azure/azure_test.go:327]; `ChatOnlyRowRoutesResponsesToChatCompletions` / `ChatOnlyRowRoutesResponsesStreamToChatCompletions` [D: core/providers/azure/azure_test.go:244,262] — Azure-specific routing between the Responses API and Chat Completions based on a model-datasheet row.
- **F-003-TC3** — `BedrockTests` [D: core/providers/bedrock/bedrock_test.go:250], `BedrockOpus47Tests` [D: core/providers/bedrock/bedrock_test.go:280], `BedrockMantleTests` [D: core/providers/bedrockmantle/bedrockmantle_test.go:104] — three separate suite entries for Bedrock's base, Opus-4.7-specific, and "Mantle" project variants.
- **F-003-TC4** — Bedrock reasoning-content assembly: `AssistantMessage_WithReasoningAndToolCalls_ReasoningComesFirst`, `AssistantMessage_WithReasoningDetails_ConvertsToBedrockReasoningContent`, `AssistantMessage_WithoutReasoningDetails_NoReasoningContent` [D: core/providers/bedrock/bedrock_test.go:4446,4380,4511] — pins the ordering and presence rules for reasoning blocks in an assistant message going to Bedrock's Converse API.
- **F-003-TC5** — Bedrock S3 document/image gating (see `data-fixtures_1.9.1_F-003.md`) [D: core/providers/bedrock/s3locationmodelgate_test.go:89,100,149,171,413].
- **F-003-TC6** — Anthropic document-block-needs-text-block guard [D: core/providers/anthropic/chat.go:1052, exercised by the surrounding chat_test.go suite].
- **F-003-TC7** — Anthropic adaptive-thinking model gate: legacy models reject `"adaptive"`, Opus/Sonnet 4.6 accept both modes [D: core/providers/anthropic/adaptivethinkingstrip_test.go:182].
- **F-003-TC8** — `CerebrasTests` [D: core/providers/cerebras/cerebras_test.go:57], `CohereTests` [D: core/providers/cohere/cohere_test.go:59] — suite entries for two further OpenAI-adjacent/non-adjacent providers, not expanded case-by-case in this pass.

This is a sample of 4385 total test cases across 454 files in `core/` [D: reverse.py survey, core/, Tests section], the large majority of which sit in `core/providers/`. Exhaustive per-case listing was out of scope for this pass; the above covers the two provider shapes (delegator, full-converter) and the specific quirks called out in `architect/feature_1.9.1_F-003_architect.md`'s Failure modes table.

## Implementation status

| Test case | Status | Evidence |
| --- | --- | --- |
| F-003-TC1 | wip — unverified, run `make test-core PROVIDER=anthropic` | `core/providers/anthropic/anthropic_test.go:82` |
| F-003-TC2 | wip — unverified, run `make test-core PROVIDER=azure` | `core/providers/azure/azure_test.go:108,244,262,327` |
| F-003-TC3 | wip — unverified, run `make test-core PROVIDER=bedrock` | `core/providers/bedrock/bedrock_test.go:250,280`, `core/providers/bedrockmantle/bedrockmantle_test.go:104` |
| F-003-TC4 | wip — unverified, run `make test-core PROVIDER=bedrock` | `core/providers/bedrock/bedrock_test.go:4446,4380,4511` |
| F-003-TC5 | wip — unverified, run `make test-core PROVIDER=bedrock` | `core/providers/bedrock/s3locationmodelgate_test.go:89,100,149,171,413` |
| F-003-TC6 | wip — unverified, no dedicated test name surfaced beyond the code comment | `core/providers/anthropic/chat.go:1052` |
| F-003-TC7 | wip — unverified, run `make test-core PROVIDER=anthropic -run TestAdaptiveThinkingStrip` | `core/providers/anthropic/adaptivethinkingstrip_test.go:182` |
| F-003-TC8 | wip — unverified, run `make test-core PROVIDER=cerebras` and `PROVIDER=cohere` | `core/providers/cerebras/cerebras_test.go:57`, `core/providers/cohere/cohere_test.go:59` |

`make test-core` hits **live provider APIs** per AGENTS.md's Testing section, so none of the above was run without the user's explicit go-ahead.

## Edge and negative cases

- Groq (delegator): calling any of the ~41 "not supported" methods — [D: core/providers/groq/groq.go, e.g. TextCompletion at groq.go:88] — no test citation found confirming the returned error shape for the unsupported path in this pass; see coverage holes below.
- Anthropic: a request that both signs incorrectly (auth failure) and carries `encrypted_content` — must not be confused with the encrypted-content strip-and-retry path [D: core/encryptedreasoning_test.go:852 — note: this file sits at `core/`, not `core/providers/`, and is F-001's territory; cited here as the boundary case for an Anthropic-specific failure mode].

## Out of scope

Live, credential-gated scenario tests (`core/internal/llmtests/`) exercise these same providers end-to-end against real APIs — covered by F-001/F-004's test plans where the scenario is cross-cutting, not duplicated here.

## OPEN

OPEN: is there a required test for every one of a provider's "not supported" stub methods (asserting the exact error shape returned), or is that left untested by convention? Not confirmed — this is a coverage hole worth flagging, not an assumption to resolve either way.
