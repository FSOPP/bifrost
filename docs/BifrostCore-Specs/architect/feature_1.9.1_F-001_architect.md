---
title: Feature Architecture 1.9.1 F-001 — Core Engine
id: F-001
kind: architecture
feature: F-001
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Feature Architecture 1.9.1 F-001 — Core Engine

> Low-level design for one feature: contracts, schema, sequence, failure modes.

## Design summary

I: Core Engine is a per-provider queueing and retry orchestrator sitting between the public `*Bifrost` API surface (data/api-contract_1.9.1_F-001.md) and the `schemas.Provider` implementations — basis: every public `*Request`/`*StreamRequest` method funnels through `handleRequest`/`handleStreamRequest` → `tryRequest`/`tryStreamRequest` → a per-provider `ProviderQueue` → a long-lived `requestWorker` goroutine → `executeRequestWithRetries` → the provider's method [D: core/bifrost.go:5271, core/bifrost.go:5577, core/bifrost.go:6929, core/bifrost.go:6192]. This rules out a directly-called (non-queued) provider path: every request, including single-key single-attempt ones, crosses a channel handoff to a fixed worker pool sized per provider [D: core/bifrost.go:166-171].

## API contracts

See data/api-contract_1.9.1_F-001.md for the full method table. In short: this layer's contract is a Go method contract, not HTTP — `*Bifrost` exposes ~60 `*Request`/`*StreamRequest` methods (`ChatCompletionRequest`, `ResponsesRequest`, `EmbeddingRequest`, `BatchCreateRequest`, `ContainerCreateRequest`, …) all converging on the same `handleRequest`/`handleStreamRequest` orchestration [D: core/bifrost.go:839, core/bifrost.go:864, core/bifrost.go:1332, core/bifrost.go:5271].

## Data model

This layer owns no persisted data. It owns two in-flight, pooled request-lifecycle types: `ChannelMessage` (one per queued request, embeds `schemas.BifrostRequest` plus response/error/stream channels and a `handoff` state) and `ProviderQueue` (one per provider, wraps the request channel with atomic shutdown signalling) [D: core/bifrost.go:62-77, core/bifrost.go:166-171]. See data/data-erd_1.9.1_F-001.md.

## Sequence

Happy path, non-streaming (`ChatCompletionRequest` as the representative case):

1. Public method (`ChatCompletionRequest`) builds a `BifrostChatRequest` and calls `handleRequest` [D: core/bifrost.go:839].
2. `handleRequest` resets per-request latency tracking, stamps a request ID if absent, runs `PluginPipeline.RunPreRequestHooks` (plugins may rewrite provider/model/fallbacks — this is the only point mutations are observed by every downstream phase) [D: core/bifrost.go:5292-5312].
3. `handleRequest` calls `tryRequest` for the primary provider [D: core/bifrost.go:5333].
4. `tryRequest` resolves the `ProviderQueue` for the provider, merges MCP tool definitions into the request if `MCPManager` is configured, runs `PluginPipeline.RunLLMPreHooks` (may short-circuit with a cached response or an error, skipping the queue entirely) [D: core/bifrost.go:5579-5652].
5. `tryRequest` acquires a pooled `ChannelMessage`, opens a "queue-wait" trace span, and sends it on `pq.queue` via a `select` that also watches `pq.done` (provider shutting down) and `ctx.Done()` (caller cancelled) and a non-blocking `default` (queue full → drop or block) [D: core/bifrost.go:5663-5736].
6. A `requestWorker` goroutine (one of a fixed pool per provider) dequeues the message, closes the queue-wait span, resolves the base provider type and per-attempt context flags, then selects a key (unless `providerRequiresKey` is false) and calls `executeRequestWithRetries` [D: core/bifrost.go:6929-7018].
7. `executeRequestWithRetries` loops up to `config.NetworkConfig.MaxRetries` (+ at most one extra attempt for the encrypted-content fail-soft, see Failure modes), calling the provider's method with the selected key each iteration [D: core/bifrost.go:6192, core/bifrost.go:6255].
8. On success, the worker calls `msg.claimDelivery()` (CAS on `handoff`) and sends the result on `msg.Response`; `tryRequest`'s `onResult` closure receives it, stamps worker-handoff latency, runs `PluginPipeline.RunPostLLMHooks`, and returns [D: core/bifrost.go:88-90, core/bifrost.go:5743-5756].
9. `handleRequest` returns the result. If the primary attempt failed and `shouldTryFallbacks` allows it, `handleRequest` loops over configured fallbacks, calling `tryRequest` again per fallback with a fresh span and a new request ID, stopping at the first success or at `shouldContinueWithFallbacks() == false` [D: core/bifrost.go:5346-5419].

## Failure modes

| Failure | Detection | Behaviour | Recovery |
| --- | --- | --- | --- |
| Provider queue full | non-blocking `default` branch on `pq.queue <-` fails | if `dropExcessRequests` is true, request dropped with `BifrostQueueFullError`; otherwise falls through to a blocking select | caller retries or operator increases queue size / `dropExcessRequests` config [D: core/bifrost.go:5707-5721] |
| Provider shutting down mid-send | `pq.isClosing()` true, or `pq.done` fires during select | message released, `"provider is shutting down"` error returned; if a replacement queue exists (provider was updated, not removed) the send is transparently re-routed to it first | caller sees the error only if no replacement queue exists [D: core/bifrost.go:5670-5736] |
| Caller context cancelled while queued | `ctx.Done()` fires in the enqueue select, or in the worker/caller handoff race | message released before a worker ever claims it, `newBifrostCtxDoneError` returned | none — request abandoned by caller [D: core/bifrost.go:5702-5706] |
| Caller context cancelled after a worker already claimed delivery | `msg.abandonDelivery()` returns false (CAS lost; `claimDelivery()` already won) | the worker, not the caller, owns billing/logging for the terminal value — `billAbandonedTerminal` runs so cost/usage isn't lost | none — this is the designed outcome of the `handoff` atomic, not an error state [D: core/bifrost.go:70-97, core/bifrost.go:7495] |
| 401/402/403 from provider (permanent per-key failure) | `lastWasPerKeyFailure`/`lastWasPermanentKeyFailure` set from the error classification | key rotated to a different credential on the next attempt; backoff suppressed since a dead key gains nothing from waiting | rotates through remaining configured keys until exhausted [D: core/bifrost.go:6234-6242] |
| 429 from provider (rate limit) | same per-key-failure classification, but not "permanent" | key rotated; backoff **not** suppressed, since account-level rate limits are shared across keys | waits out backoff, retries with rotated key [D: core/bifrost.go:6234-6242] |
| Request-bound 4xx (other), success codes, transient 5xx, 529 | excluded from the per-key-failure classification | key is **not** rotated — burning other keys on a problem that isn't the key's fault would multiply failures | same key retried per normal backoff, or error surfaces if retries exhausted [D: core/bifrost.go:6234-6242, per stated constraint at core/bifrost_test.go:804] |
| Provider rejects encrypted `reasoning` content on replay | upstream 400 whose envelope matches the widened detector, and `encrypted_content` present in the request | `encrypted_content` stripped from the request and exactly one extra attempt granted outside the normal retry budget (`extraAttempts`), so a persistently-rejecting upstream cannot loop | fires at most once per request (`strippedEncryptedContent` latch) [D: core/bifrost.go:6255, core/bifrost.go:6249-6252] |
| All fallbacks exhausted | fallback loop completes without an early return | original primary error returned to caller | none — surfaced to caller [D: core/bifrost.go:5417-5419] |

## Observability

- Trace spans: `handle-setup`, `miscellaneous` (multiple, per phase), `pipeline-pre`, `pipeline-post`, `worker-setup`, a per-fallback span named `fallback.<provider>.<model>`, and a "queue-wait" span opened at enqueue / closed at dequeue [D: core/bifrost.go:5301, core/bifrost.go:5316, core/bifrost.go:5609, core/bifrost.go:5753, core/bifrost.go:6976, core/bifrost.go:5372, core/bifrost.go:8796].
- Routing engine audit log: `ctx.AppendRoutingEngineLog(schemas.RoutingEngineCore, ...)` records fallback transitions, retry exhaustion, and cancellation/timeout outcomes with the triggering error summarized via `routingErrorSummary` [D: core/bifrost.go:5355, core/bifrost.go:5410, core/bifrost.go:6212-6226].
- Debug logs never include raw request/response bodies directly — the code comment is explicit that `GetErrorString()` (not `%v` on the error) must be used because `ExtraFields.RawRequest/RawResponse` can carry the Authorization header or a Vertex/Gemini `?key=` query param [D: core/bifrost.go:5335-5339].

## Traceability

- PRDs/prd_1.9.1_F-001-core-engine.md — stories inferred from this sequence and the tests below.
- domain_DOM-001-core-engine.md — ChannelMessage handoff exclusivity and key-rotation rules as domain invariants.

OPEN: no SLO/target latency or throughput number is expressed anywhere in this code path (queue depth, worker count, and MaxRetries are operator-configured, not fixed) — is there a target p95 or RPS this design was sized against?
