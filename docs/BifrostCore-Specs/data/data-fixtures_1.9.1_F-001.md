---
title: Data Fixtures 1.9.1 F-001 — Core Engine
id: F-001
status: draft
owner: TBD
updated: 2026-09-21
---

# Data Fixtures 1.9.1 F-001 — Core Engine

> The test data this feature is implemented and verified against, and what each fixture is for.

## Fixture sets

D: this Go test suite builds `ChannelMessage`/`schemas.BifrostRequest` fixtures as in-code struct literals per test function, not as external JSON/YAML fixture files — no `testdata/*.json` fixture directory was found under core/ root by the survey. A representative minimal set, reconstructed as JSON for this document only (not present verbatim in the repo):

| Set ID | Entity | Scenario | Test case |
| --- | --- | --- | --- |
| F-001-FX1 | `ChannelMessage` (handoff race) | worker claims delivery before caller context ends | `TestChannelMessageHandoffIsExclusive` [D: core/abandonedstream_test.go:443] |
| F-001-FX2 | key-attempt sequence | 401/403 permanent failure → rotate; 429 → rotate+backoff; 5xx/529 → same key | key-rotation test at [D: core/bifrost_test.go:804] |
| F-001-FX3 | `ChannelMessage` pool reset | idle pooled message must not pin request-scoped references | `releaseChannelMessage` test [D: core/bifrost_test.go:3555] |

## Fixture file

I: `fixtures/fixtures_1.9.1_F-001.json` is left as the scaffold's empty template — basis: no JSON/YAML fixture files exist in core/'s test tree for this scope, so there is nothing to transcribe without inventing data. Populating it would mean writing fixtures that do not exist in the codebase.

## Encoded invariants

- Exactly one side of the handoff wins (`claimDelivery` XOR `abandonDelivery`) — never both, never neither [D: core/bifrost.go:88-97].
- A dead/rejected key (401/403) triggers rotation without backoff; a rate-limited key (429) triggers rotation with backoff; a transient error (5xx/529) never triggers rotation [D: core/bifrost.go:6234-6242].

## Determinism rules

OPEN: whether the Go test suite's struct-literal fixtures use fixed IDs/timestamps or `time.Now()`/`uuid.New()` at test time was not verified line-by-line in this pass — would require reading each `_test.go` file individually rather than the survey's citation index.

## Loading

D: fixtures are constructed inline in Go test functions (`go test ./core/...`), not loaded from an external file or seeded into a store — there is no store to reset for this in-memory-only feature.

## Traceability

- F-001-FX1 → `test_1.9.1_F-001.md`'s TC row for `TestChannelMessageHandoffIsExclusive`.
- F-001-FX2 → the key-rotation TC row.
- F-001-FX3 → the pool-reset TC row.

OPEN: should this feature adopt external JSON fixtures for these scenarios, or is the in-code struct-literal pattern the team's deliberate convention for a library with no persistence layer? Not recoverable from code — a style choice, not a behavior.
