---
title: API Contract 1.9.1 F-002 — Provider Abstraction
id: F-002
status: draft
owner: TBD
updated: 2026-09-21
---

# API Contract 1.9.1 F-002 — Provider Abstraction

> The wire contract for this feature — the readable companion to its OpenAPI and AsyncAPI files.

## Surface summary

I: this is a Go interface contract, not an HTTP one — basis: the survey of `core/` found 0 HTTP endpoints (core is the library; HTTP routing lives in `transports/bifrost-http`, out of this feature's scope) [D: survey.md "HTTP surface: none found"]. The real contract F-002 exposes is `schemas.Provider` (`provider.go:681-800`): every one of the 20+ providers under `core/providers/` must implement all methods below in full — an unsupported operation still needs a method body, it just returns a typed error [D: providers/groq/groq.go:88-90]. `openapi_1.9.1_F-002.json` and `asyncapi_1.9.1_F-002.json` are marked N/A for this feature (left as scaffold stubs) — there is no wire-level JSON contract to describe here.

## Endpoints

Not applicable — see Surface summary. In place of HTTP endpoints, the table below is the `Provider` interface's method inventory (30 methods, `provider.go:681-800`), one row per method, D-cited:

| Method | Purpose | Optional / required |
| --- | --- | --- |
| `GetProviderKey` | Returns the provider's `ModelProvider` identifier | required [D: provider.go:683] |
| `ListModels` | Lists models available from the provider | required [D: provider.go:685] |
| `TextCompletion` / `TextCompletionStream` | Legacy text completion, unary and streaming | required [D: provider.go:687-692] |
| `ChatCompletion` / `ChatCompletionStream` | OpenAI-shaped chat completion | required [D: provider.go:694-696] |
| `Responses` / `ResponsesStream` | OpenAI Responses API (internally rebuilt from chat completion for non-OpenAI providers) | required [D: provider.go:698-700] |
| `CountTokens` | Token counting against a Responses-shaped request | required [D: provider.go:702] |
| `Compaction` | Conversation compaction — OpenAI-only, others return unsupported [D: provider.go:703-704] | required (method), OpenAI-only (behaviour) |
| `Embedding`, `Rerank`, `OCR` | Embedding, rerank, OCR requests | required [D: provider.go:706-710] |
| `Speech` / `SpeechStream`, `Transcription` / `TranscriptionStream` | TTS / STT, unary and streaming | required [D: provider.go:712-718] |
| `ImageGeneration`/`Stream`, `ImageEdit`/`Stream`, `ImageVariation` | Image operations | required [D: provider.go:719-731] |
| `VideoGeneration`, `VideoEdit`, `VideoRetrieve`, `VideoDownload`, `VideoDelete`, `VideoList`, `VideoRemix` | Video job lifecycle | required [D: provider.go:732-745] |
| `BatchCreate/List/Retrieve/Cancel/Delete/Results` | Async batch job lifecycle | required [D: provider.go:746-757] |
| `FileUpload/List/Retrieve/Delete/Content` | File management | required [D: provider.go:758-767] |
| `CachedContentCreate/List/Retrieve/Update/Delete` | Gemini/Vertex named-cache lifecycle | required [D: provider.go:768-777] |
| `ContainerCreate/List/Retrieve/Delete`, `ContainerFileCreate/List/Retrieve/Content/Delete` | Container + container-file lifecycle | required [D: provider.go:778-795] |
| `Passthrough` / `PassthroughStream` | Raw request passthrough, buffered and streamed | required [D: provider.go:796-799] |
| `ResponsesRetrieve/Delete/Cancel/InputItems`, `ResponsesRetrieveStream` | Responses-API secondary verbs | **optional** — separate `ResponsesLifecycleProvider` interface, checked via type assertion; non-implementers return `unsupported_operation` [D: provider.go:802-812] |
| `SupportsResponsesNamespaceTools` | Whether `namespace` tools are supported for a given (key, model) routing | **optional** — `ResponsesNamespaceToolProvider`, e.g. Bedrock differs by whether a call routes to Mantle or Converse [D: provider.go:814-823] |
| `SupportsWebSocketMode`, `WebSocketResponsesURL`, `WebSocketHeaders` | WebSocket-mode Responses API support | **optional** — `WebSocketCapableProvider` [D: provider.go:825-837] |

I: Groq is a representative "mostly not-supported" implementer for legacy/non-chat verbs — basis: `TextCompletion`, `Embedding`, `Rerank`, `OCR`, `SpeechStream`, `TranscriptionStream`, `ImageGeneration*`, `ImageEdit*` are each a one-line `return nil, providerUtils.NewUnsupportedOperationError(...)` [D: providers/groq/groq.go:88-90, :171, :196, :201, :206, :230, :235, :240, :245, :250]. `OPEN:` which providers implement the full 30-method surface without any unsupported stub? Not determined here — would require a per-provider grep pass out of this feature's evidence budget.

## Events

None. `core/schemas` defines no pub/sub channels; the 5 event-shaped string literals the survey found (`human`, `exchange`, `rfc8693`, `jwt_bearer_obo`, `queued`) are declared-but-unused message constants, not live topics [D: survey.md "Events / topics" — schemas/mcp.go:56, schemas/oauth.go:119, :124, schemas/responses.go:1280].

## Error model

One shape, `BifrostError` (`bifrost.go:1954-1963`): `EventID`, `Type`, `IsBifrostError bool`, `StatusCode`, `Error *ErrorField`, `AllowFallbacks *bool` (nil/true = allow fallbacks, false = block — `AGENTS.md` "Plugin System"), `StreamControl`, `ExtraFields BifrostErrorExtraFields` (carries `RequestType`, `Provider`, `OriginalModelRequested`, `ResolvedModelUsed`, populated by `PopulateExtraFields` both before and after post-hooks so plugin tampering with those four fields is a no-op) [D: bifrost.go:1954-1974]. Every provider's "not supported" return uses this same shape via `providerUtils.NewUnsupportedOperationError` [D: providers/groq/groq.go:89]. `OPEN:` the exact status-code-to-condition mapping is provider-specific and lives in each provider's `errors.go`, out of scope for this feature.

## Versioning and compatibility

`OPEN:` no version-negotiation or deprecation-window logic exists in `core/schemas` itself. `NetworkConfig.UnmarshalJSON` does carry one real backward-compatibility rule: `RetryBackoffInitial`/`RetryBackoffMax` accept either a duration string (preferred) or a legacy bare integer read as milliseconds [D: provider.go:56-59, 85-148] — the only "may not change without breaking a caller" contract found in this feature's evidence.

## Spec files

`schema/openapi_1.9.1_F-002.json` and `schema/asyncapi_1.9.1_F-002.json` — N/A, left as scaffold stubs (see Surface summary). The Go interface in `provider.go` and the struct definitions across `core/schemas/*.go` are this feature's actual spec; there is no generated OpenAPI for core's own Go contract.

## Traceability

`F-002-US1` (implement the interface once, run against every operation), `F-002-US2` (optional-interface capability detection), `F-002-US3` (context-based cross-cutting state) — see `PRDs/prd_1.9.1_F-002-provider-abstraction.md`.
