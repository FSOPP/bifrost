---
title: Route 1.9.1 F-002 — Provider Abstraction
id: F-002
status: draft
owner: TBD
updated: 2026-09-21
---

# Route 1.9.1 F-002 — Provider Abstraction

> Agent entrypoint: the exact documents to read, in order, before touching this feature.

## Objective

Any agent changing the `Provider` interface, `BifrostContext`, plugin interfaces, or a `Bifrost*Request`/`Bifrost*Response` type family must read this route first — a change here compiles against 543 provider files and every request path in the engine (AGENTS.md gotcha #5, #6).

## Required reading (in order)

1. `docs/BifrostCore-Specs/data/data-erd_1.9.1_F-002.md` — the entity/struct inventory this feature owns.
2. `docs/BifrostCore-Specs/data/api-contract_1.9.1_F-002.md` — the `Provider` interface's full method surface and the optional-interface pattern.
3. `docs/BifrostCore-Specs/architect/feature_1.9.1_F-002_architect.md` — reserved-key guard, plugin pipeline symmetry, failure modes.
4. `docs/BifrostCore-Specs/PRDs/prd_1.9.1_F-002-provider-abstraction.md` — why the interface is shaped this way.
5. `docs/BifrostCore-Specs/tests/test_1.9.1_F-002.md` — existing coverage before adding a method.
6. Root `AGENTS.md`, section "Adding a New Provider — Full Checklist" and "Gotcha #5: Provider Interface Has 30+ Methods" — the cross-package cascade a change here triggers.

## Guardrails

Do not add a method to `Provider` without also adding a "not supported" stub to every existing provider that doesn't implement it (AGENTS.md gotcha #5). Do not add a new context key without deciding whether it belongs in `reservedKeys` (context.go:19-45) — a key that should be Bifrost-internal but isn't reserved is silently overwritable by any plugin. Stop and ask before changing `NetworkConfig`'s JSON wire format — its `UnmarshalJSON` carries an explicit backward-compatibility contract (duration string vs. legacy integer-milliseconds).

## Exit criteria

`go build ./core/...` succeeds; `go vet ./core/...` is clean; every provider package still compiles against the (possibly extended) `Provider` interface.

## Rule file

<!-- `rule_1.9.1_F-002.json` — generated, machine-readable form of the above. -->

TBD
