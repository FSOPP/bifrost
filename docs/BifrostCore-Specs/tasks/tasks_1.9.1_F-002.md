---
title: Tasks 1.9.1 F-002 — Provider Abstraction
id: F-002
kind: tasks
feature: F-002
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Tasks 1.9.1 F-002 — Provider Abstraction

> Ordered, dependency-aware implementation tasks — plan only, no code.

> As-built inventory — every row below already exists in the repository. `done-when` states the check that *would* prove it; status is set from evidence per `status-model.md`, not from the fact that the code is visibly present.

## Task list

| Task ID | Description | Depends-on | Artifact | Done-when | Status |
| --- | --- | --- | --- | --- | --- |
| F-002-T1 | Define `Provider` interface (30 methods + 3 optional capability interfaces) | — | `core/schemas/provider.go:681-837` | `go build ./core/...` succeeds and every provider under `core/providers/` compiles against it | wip — unverified, run `go build ./core/...` |
| F-002-T2 | Implement `BifrostContext`: thread-safe values, reserved-key guard, deadline/cancellation, plugin scoping | F-002-T1 | `core/schemas/context.go` | `go test ./core/schemas/... -run TestBifrostContext` green | wip — unverified, run `go test ./core/schemas/... -run TestBifrostContext` |
| F-002-T3 | Define `LLMPlugin`/`MCPPlugin`/`HTTPTransportPlugin`/`ObservabilityPlugin` interfaces + pipeline ordering contract | F-002-T1 | `core/schemas/plugin.go` | `go test ./core/schemas/... -run TestPlugin` green | wip — unverified, run `go test ./core/schemas/... -run TestPlugin` |
| F-002-T4 | Define `NetworkConfig`/`ProviderConfig`/`CustomProviderConfig`/`AllowedRequests` + defaulting/redaction logic | — | `core/schemas/provider.go:53-676` | `go test ./core/schemas/... -run TestProxyConfigRedaction` green | wip — unverified, run `go test ./core/schemas/... -run TestProxyConfigRedaction` |
| F-002-T5 | Define request/response type families (chat, responses, embedding, images, batch, files, videos, containers, cached contents, speech, transcription, passthrough) | F-002-T1 | `core/schemas/{chatcompletions,responses,embedding,images,batch,files,videos,containers,cachedcontents,speech,transcriptions,passthrough}.go` | `go test ./core/schemas/... -run TestSerialization` green | wip — unverified, run `go test ./core/schemas/... -run TestSerialization` |

## Execution order

F-002-T1 → { F-002-T2, F-002-T3, F-002-T5 } (parallelizable once the interface exists) ; F-002-T4 has no dependency on F-002-T1 and could be built independently. I: this ordering is inferred from import direction, not from any commit-history reconstruction — `git log`-based sequencing was not attempted (see filling.md's caution on history precision).

## Definition of done

Per `status-model.md`: code exists (D), a test name covers it (D), and the repository's own `go test` command for the covering test was run in this environment and passed (the gate this pass did not clear — see report).
