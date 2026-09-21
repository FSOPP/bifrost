---
title: Data Fixtures 1.9.1 F-002 — Provider Abstraction
id: F-002
status: draft
owner: TBD
updated: 2026-09-21
---

# Data Fixtures 1.9.1 F-002 — Provider Abstraction

> The test data this feature is implemented and verified against, and what each fixture is for.

## Fixture sets

I: `core/schemas` has no persisted fixture files of its own (no `testdata/` directory found under it) — basis: fixtures for this package are constructed inline as Go literals inside each `_test.go` file, table-driven style [D: schemas/modelcapabilities_test.go — `AbsentFallsBack`, `AbsentRowFallsBack`, `CallerFallbackUsedWhenRowIsSilent` subtests at survey.md lines 89-90, 118-119]. The JSON fixture set below is this document's own minimal-valid-record rendering (`I:`), not extracted from a repository JSON fixture that doesn't exist.

| Set ID | Entities | Scenario | Test cases |
| --- | --- | --- | --- |
| F-002-FX1 | Key | minimal enabled key | I: represents the zero-config case a `ProviderConfig` selects against |
| F-002-FX2 | BifrostChatRequest / BifrostChatResponse | one round trip pair | I: shape a `Provider.ChatCompletion` implementer must accept/return |
| F-002-FX3 | BifrostError | unsupported-operation error | D: shape returned by `providerUtils.NewUnsupportedOperationError` [providers/groq/groq.go:89] |

## Fixture file

See `fixtures/fixtures_1.9.1_F-002.json`. `OPEN:` these records validate against the `Key`/`BifrostChatRequest`/`BifrostChatResponse`/`BifrostError` shapes as documented in `data-erd_1.9.1_F-002.md`, but `schema/schemas.json`'s `$defs` do not yet contain those entity names (shared file, out of this fork's write scope — see coordination note in the data-erd document). `route.py`'s fixture validation will not pass against the current shared `schemas.json` until that shared update lands.

## Encoded invariants

- F-002-FX1 exercises `Enabled *bool` being unset (nil) vs. explicitly `false` — I: the pointer type exists specifically to distinguish "not specified, default true" from "explicitly disabled" [basis: every other boolean-flag field in `Key` that has a stated default uses `*bool`, e.g. `UseForBatchAPI` — D: account.go:154].
- F-002-FX3 exercises the "not supported" error path rather than a genuine provider failure — the same `BifrostError` shape carries both.

## Determinism rules

Fixed IDs (`"key-fixture-001"`, no UUID generation), no timestamps requiring `time.Now()`, no live API keys (`Value` fields use an obviously-fake literal, never a real secret).

## Loading

`OPEN:` `core/schemas` has no fixture-loading harness — its own tests build literals directly in Go. This JSON file exists for the docs hub's `route.py` validation step, not for a Go test to load; no in-repo loader references it.

## Traceability

F-002-TC (see `tests/test_1.9.1_F-002.md`) — the schemas package's own tests don't consume this file; it is a docs-hub artifact only. Flagged as an `OPEN:` gap between hub convention and how this particular package actually tests itself.
