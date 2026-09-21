---
title: Route 1.9.1 F-003 — Provider Implementations
id: F-003
status: draft
owner: TBD
updated: 2026-09-21
---

# Route 1.9.1 F-003 — Provider Implementations

> Agent entrypoint: the exact documents to read, in order, before touching this feature.

## Objective

Prepare an agent to modify or extend a provider implementation in `core/providers/` — fixing a converter bug, adding a new operation to an existing provider, or adding a new provider package — without breaking the shared `Provider` interface contract or the delegator packages that depend on `openai.HandleOpenAI*`.

## Required reading (in order)

1. `data/data-erd_1.9.1_F-003.md` — confirms this feature owns no persisted entity; skip expecting a database.
2. `data/api-contract_1.9.1_F-003.md` — the real contract is the `Provider` interface method coverage, not HTTP.
3. `architect/architect_common.md` — repo-wide conventions (converter naming, `fasthttp` not `net/http`, `sonic`/`gjson` JSON rules).
4. `architect/feature_1.9.1_F-003_architect.md` — the two provider shapes, the sequence, and the known failure-mode guards.
5. `ddd/domain_DOM-001-core-engine.md` — cross-cutting invariants that apply across providers (if any touch this feature).
6. `tests/test_1.9.1_F-003.md` — existing coverage and coverage holes before adding more.
7. `tasks/tasks_1.9.1_F-003.md` — as-built inventory.
8. `PRDs/prd_1.9.1_F-003-provider-implementations.md` — the "why" behind the delegator/full-converter split.

## Guardrails

- Never change `openai.HandleOpenAI*` function signatures without checking all 9+ delegator packages that call them (AGENTS.md Gotcha #6).
- Never call `make test-core` (any provider) without the user's explicit go-ahead — it hits live provider APIs and can cost money.
- Keep converter functions pure — no HTTP calls, no logging, inside `To<Provider><Feature>Request`/`ToBifrost<Feature>Response`.
- Stop and ask if a change would require adding a method to `schemas.Provider` itself — that's F-002's contract, not this feature's.

## Exit criteria

Cited test(s) for the changed provider pass under `make test-core PROVIDER=<name>` (run by the user, not the agent), and any new "not supported" or newly-supported method is reflected in `data/api-contract_1.9.1_F-003.md`'s coverage note.

## Rule file

`rule_1.9.1_F-003.json` — generated, machine-readable form of the above.
