---
title: Data Model 1.9.1 F-001 — Core Engine
id: F-001
status: draft
owner: TBD
updated: 2026-09-21
---

# Data Model 1.9.1 F-001 — Core Engine

> The slice of the data model this feature reads and writes, at field precision.

## Scope

D: this is not a persisted data model — core/ has no database, no ORM, no migrations (survey found exactly one low-confidence, unextractable "entity" in `providers/gemini/types.go:1345`, out of this feature's scope). F-001 owns two **in-flight, pooled, request-lifecycle types**, both reset-and-returned to a `sync.Pool` rather than persisted [D: core/bifrost.go:115-120]:

| Entity | Own / Read / Write | Lifetime |
| --- | --- | --- |
| `ChannelMessage` | owns | one per queued request; acquired from `bifrost.channelMessagePool`, released via `releaseChannelMessage` [D: core/bifrost.go:8815, core/bifrost.go:8896] |
| `ProviderQueue` | owns | one per configured provider; created in `prepareProvider`/`getProviderQueue`, lives until `RemoveProvider`/`UpdateProvider`/`Shutdown` drops the last reference [D: core/bifrost.go:4592, core/bifrost.go:4643] |
| `schemas.BifrostRequest` | reads/writes | embedded by value inside `ChannelMessage`; pooled separately via `bifrostRequestPool` [D: core/bifrost.go:63, core/bifrost.go:8946-9008] |
| `schemas.BifrostContext` | reads/writes | not owned by this feature (defined in core/schemas/context.go) but is the vehicle for every per-request value this layer sets (fallback index, request ID, retry count, routing engine log) [D: core/bifrost.go:5292-5296, core/bifrost.go:6259] |

## Feature ERD

See `schema/erd_1.9.1_F-001.puml` — a request-lifecycle diagram (ChannelMessage → ProviderQueue → worker), not an entity-relationship diagram over persisted tables, since none exist here.

## Field definitions

| Entity | Field | Type | Constraint | Nullable | Notes |
| --- | --- | --- | --- | --- | --- |
| `ChannelMessage` | `schemas.BifrostRequest` (embedded) | struct | — | no | the request being carried [D: core/bifrost.go:63] |
| `ChannelMessage` | `Context` | `*schemas.BifrostContext` | — | no (set immediately after acquire) | [D: core/bifrost.go:64, core/bifrost.go:5664] |
| `ChannelMessage` | `Response` | `chan *schemas.BifrostResponse` | cap 1 | no | drained on acquire so a worker's send is always ready [D: core/bifrost.go:65, core/bifrost.go:70-72] |
| `ChannelMessage` | `ResponseStream` | `chan chan *schemas.BifrostStreamChunk` | — | no | streaming path only [D: core/bifrost.go:66] |
| `ChannelMessage` | `Err` | `chan schemas.BifrostError` | cap 1 | no | [D: core/bifrost.go:67] |
| `ChannelMessage` | `queueSpan` | `schemas.SpanHandle` | — | yes (nil if tracer absent) | opened at enqueue, closed at dequeue or release [D: core/bifrost.go:68] |
| `ChannelMessage` | `sentAt` | `time.Time` | — | zero value = unset | stamped by worker immediately before sending the result [D: core/bifrost.go:69] |
| `ChannelMessage` | `handoff` | `atomic.Int32` (enum: open/claimed/abandoned) | CAS-guarded, exactly one winner | no | see DOM-001-core-engine.md for the invariant this enforces [D: core/bifrost.go:76, core/bifrost.go:79-83] |
| `ProviderQueue` | `queue` | `chan *ChannelMessage` | never closed (see code comment rationale) | no | [D: core/bifrost.go:167] |
| `ProviderQueue` | `done` | `chan struct{}` | closed exactly once via `signalOnce` | no | [D: core/bifrost.go:168, core/bifrost.go:170-195] |
| `ProviderQueue` | `closing` | `uint32` (atomic 0/1) | — | no | [D: core/bifrost.go:169] |

## New and changed entities

Not applicable in the master-ERD sense — see data-master-erd.md, which records these as request-lifecycle types rather than registry rows with FK relations, since neither has a foreign key or a persistence boundary.

## Migrations

N/A — no schema migrations; these are in-memory Go structs.

## Traceability

- DOM-001-core-engine.md — the `handoff` field is the direct implementation of the "exactly one side wins" domain rule.
- PRDs/prd_1.9.1_F-001-core-engine.md — F-001-US stories reference `ChannelMessage` pooling and `ProviderQueue` shutdown semantics.

OPEN: no capacity/backpressure default (queue buffer size) is visible in this file — is it a fixed constant or fully operator-configured via `NetworkConfig`? Not confirmed by this survey pass; would require reading `prepareProvider`/`Init` config wiring in full.
