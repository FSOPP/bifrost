---
title: Data Fixtures 1.9.1 F-003 — Provider Implementations
id: F-003
status: draft
owner: TBD
updated: 2026-09-21
---

# Data Fixtures 1.9.1 F-003 — Provider Implementations

> The test data this feature is implemented and verified against, and what each fixture is for.

## Fixture sets

`fixtures/fixtures_1.9.1_F-003.json` is empty by design (see `data-erd_1.9.1_F-003.md` — no persisted entities). This feature's real test data lives in each provider package's own Go test files as literal request/response fixtures, sampled here rather than exhaustively catalogued:

| Set | Scenario it represents | Test cases |
| --- | --- | --- |
| Bedrock S3 document/image location gating | Chat requests referencing an S3-hosted document or image, and the model-support gate for that path | `ChatDocument` [D: core/providers/bedrock/s3locationmodelgate_test.go:89,149], `ChatImage` [D: core/providers/bedrock/s3locationmodelgate_test.go:100,171], `Chat` [D: core/providers/bedrock/s3locationmodelgate_test.go:413] |
| Vertex Anthropic-on-Vertex batch conversion | Converting a batch request between native Anthropic and OpenAI-shaped bodies when Anthropic models run through Vertex | `AnthropicConvertsOpenAIBodyAndUsesNativeCustomID`, `AnthropicConvertsOpenAIOnlyFields`, `AnthropicKeepsSharedFieldsAsNative`, `AnthropicPassesThroughNativeBodyAndDropsModel`, `AnthropicPreservesExistingAnthropicVersion` [D: core/providers/vertex/batch_conversion_test.go:171,203,254,280,307] |

## Fixture file

`fixtures/fixtures_1.9.1_F-003.json` — intentionally empty (`$comment` only). Every provider package's own `_test.go` file is its own fixture source; there is no shared fixture file for this feature.

## Encoded invariants

The Bedrock S3 gating fixtures exercise the rule that not every model can accept an S3-referenced (as opposed to inline) document or image — the test names imply a per-model capability check, though the exact gating table was not read in this pass. The Vertex batch fixtures exercise five distinct edge cases around dual-format (OpenAI-shaped vs native-Anthropic) batch request handling on one upstream.

## Determinism rules

Not assessed in this pass — would require reading each cited test file's fixture literals for hard-coded IDs/timestamps vs generated values.

## Loading

Each is a Go table-driven or fixture-literal test loaded by `go test`; there is no shared fixture-loading harness for `core/providers/` as a whole — [D: reverse.py survey, core/, "test discovery config: none — file conventions only"].

## Traceability

`F-003-TC*` in `tests/test_1.9.1_F-003.md`.

## OPEN

OPEN: is there a project convention for what "determinism" means for provider fixtures (e.g. banning wall-clock reads in test data), or is that left to each contributor? Not stated anywhere found in `core/providers/`.
