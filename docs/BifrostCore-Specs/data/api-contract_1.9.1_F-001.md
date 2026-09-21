---
title: API Contract 1.9.1 F-001 — Core Engine
id: F-001
status: draft
owner: TBD
updated: 2026-09-21
---

# API Contract 1.9.1 F-001 — Core Engine

> The wire contract for this feature — the readable companion to its OpenAPI and AsyncAPI files.

## Surface summary

D: core/ has zero HTTP routes — `reverse.py survey` scoped to this module found no route registrations of any kind [D: survey.md "HTTP surface: none found"]. Core is a Go library; the HTTP transport that exposes Bifrost over the wire lives in `transports/bifrost-http/` (out of scope for this feature — see AGENTS.md's "Request Flow"). What F-001 actually exposes is a **Go method contract**: the exported methods of `*bifrost.Bifrost`, called in-process by `transports/bifrost-http/handlers/` or directly by an SDK consumer. schema/openapi_1.9.1_F-001.json and schema/asyncapi_1.9.1_F-001.json are marked N/A below — there is no REST or async wire surface at this layer to describe.

## Endpoints

N/A — no HTTP endpoints. The nearest analogue is the exported method table on `*bifrost.Bifrost` (core/bifrost.go). Representative subset, cited by signature line:

| Method | Request type | Response type | Notes |
| --- | --- | --- | --- |
| `ChatCompletionRequest` | `*schemas.BifrostChatRequest` | `*schemas.BifrostChatResponse` | [D: core/bifrost.go:839] |
| `ChatCompletionStreamRequest` | `*schemas.BifrostChatRequest` | `chan *schemas.BifrostStreamChunk` | [D: core/bifrost.go:864] |
| `ResponsesRequest` | `*schemas.BifrostResponsesRequest` | `*schemas.BifrostResponsesResponse` | [D: core/bifrost.go:941] |
| `EmbeddingRequest` | `*schemas.BifrostEmbeddingRequest` | `*schemas.BifrostEmbeddingResponse` | [D: core/bifrost.go:1332] |
| `BatchCreateRequest` / `BatchListRequest` / `BatchRetrieveRequest` / `BatchCancelRequest` / `BatchDeleteRequest` / `BatchResultsRequest` | per-op request struct | per-op response struct | [D: core/bifrost.go:2331-2590] |
| `FileUploadRequest` / `FileListRequest` / `FileRetrieveRequest` / `FileDeleteRequest` / `FileContentRequest` | per-op request struct | per-op response struct | [D: core/bifrost.go:2590-2804] |
| `ContainerCreateRequest` … `ContainerFileDeleteRequest` (8 methods) | per-op request struct | per-op response struct | [D: core/bifrost.go:3063-3456] |
| `Passthrough` / `PassthroughStream` | raw bytes | raw bytes / stream | opaque pass-through, bypasses conversion [D: core/bifrost.go:2920, core/bifrost.go:2955] |

I: every method above funnels through the shared `handleRequest`/`handleStreamRequest` orchestration described in feature_1.9.1_F-001_architect.md — basis: each method's body is a thin request-struct assembly followed by a call to `handleRequest` or `handleStreamRequest` [D: core/bifrost.go:839, core/bifrost.go:5271]. Full method inventory (~60 methods) is derivable by grepping `func (bifrost \*Bifrost)` in core/bifrost.go; not reproduced row-by-row here per the "cite the file, don't restate it" rule.

## Events

Empty, stated. The survey's 5 detected "events" in core/ (`human`, `exchange`, `rfc8693`, `jwt_bearer_obo`, `queued`) are all `confidence: declared, unused` string literals inside OAuth/response-schema type files, not a pub/sub channel this feature publishes or subscribes to [D: survey.md "Events / topics", schemas/oauth.go:119, schemas/oauth.go:124, schemas/responses.go:1280]. There is no message-broker or event-bus integration in core/.

## Error model

Single shape: `*schemas.BifrostError`, carrying `IsBifrostError bool`, an optional `*ErrorField` (`Message`, `Type`), and `ExtraFields` (`RequestType`, `Provider`, `OriginalModelRequested`, `ResolvedModelUsed`, plus latency/routing metadata) [D: core/bifrost.go:5581-5582, core/bifrost.go:6955-6964]. `IsBifrostError` distinguishes an internal/orchestration error (queue full, provider shutting down, context done) from an error the upstream provider actually returned. Two internally-classified error types are checked explicitly in the retry-exhaustion path: `schemas.RequestCancelled` and `schemas.RequestTimedOut` [D: core/bifrost.go:6218-6221]. See Failure modes in feature_1.9.1_F-001_architect.md for which condition produces which error.

## Versioning and compatibility

OPEN: no version-compatibility policy for the `*bifrost.Bifrost` Go API is stated anywhere in core/ (no `CHANGELOG.md` deprecation notes were surveyed in this module, though `core/changelog.md` exists — see In-repo documents). Whether adding a field to a request struct, or adding a new method, is treated as a breaking change for SDK consumers is not recoverable from code.

## Spec files

- schema/openapi_1.9.1_F-001.json — N/A, left as the scaffold template (no REST surface).
- schema/asyncapi_1.9.1_F-001.json — N/A, left as the scaffold template (no async surface).
- Request/response struct shapes are defined in `core/schemas/*.go` (chatcompletions.go, responses.go, embedding.go, batch.go, files.go) and are the actual $ref targets a schemas.json for this module would point to (see data-erd_1.9.1_F-001.md).

## Traceability

- PRDs/prd_1.9.1_F-001-core-engine.md stories reference the methods and failure modes documented above.

OPEN: is `transports/bifrost-http`'s HTTP contract (which does exist, per AGENTS.md's handler list) meant to be documented as a sibling F-00x feature in a future reverse-docs pass over `transports/`? This hub's scope was deliberately limited to `core/` and does not cover it.
