---
title: Tasks 1.9.1 F-003 — Provider Implementations
id: F-003
kind: tasks
feature: F-003
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Tasks 1.9.1 F-003 — Provider Implementations

> Ordered, dependency-aware implementation tasks — plan only, no code.

This is an **as-built inventory**: every row describes work already shipped, grouped by the two provider shapes from `architect/feature_1.9.1_F-003_architect.md`, not a forward plan.

## Task list

| Task | Description | Depends on | Artifact | Done-when | Status |
| --- | --- | --- | --- | --- | --- |
| F-003-T1 | Non-OpenAI-compatible providers implement their own request/response converters and error parsers (Anthropic, Bedrock, Gemini, Vertex, Cohere, Azure, etc.) | F-002 (Provider interface) | `core/providers/anthropic/`, `core/providers/bedrock/`, … [D: module layout, providers = 543 files] | `make test-core PROVIDER=<name>` green for each provider | todo |
| F-003-T2 | OpenAI-compatible providers delegate to `openai.HandleOpenAI*` functions instead of re-implementing converters (Groq, Cerebras, Ollama, Perplexity, OpenRouter, Parasail, Nebius, xAI, SGL) | F-003-T1 (openai package itself is a full-converter implementation) | `core/providers/groq/groq.go:101-116` and siblings | `make test-core PROVIDER=<name>` green for each delegator | todo |
| F-003-T3 | Streaming/unary dual-client split applied per provider (`BuildStreamingClient`) | F-003-T1, F-003-T2 | `core/providers/*/*.go` constructor functions | Streaming requests use `streamingClient`, confirmed by `providers/anthropic/anthropic.go:1514` pattern replicated per package | todo |
| F-003-T4 | Provider-specific failure-mode guards (Anthropic document-block placeholder, adaptive-thinking gate) | F-003-T1 | `core/providers/anthropic/chat.go:1052`, `core/providers/anthropic/adaptivethinkingstrip_test.go:182` | Guard exercised by a passing test citing the same lines | todo |

Status left at `todo` for every row — no test run performed in this pass (see `tests/test_1.9.1_F-003.md`). Moving any row to `wip`/`done` must go through `product-docs-flow/scripts/docs_flow.py task --feature F-003 --version 1.9.1 --id F-003-T<k> --state <state>` after the cited command is actually run; not done here since `make test-core` reaches live provider APIs (AGENTS.md), which this reverse-docs pass did not run without confirmation.

## Execution order

F-003-T1 and F-003-T2 do not depend on each other directly but both depend on F-002 (the `Provider` interface they implement) and, for T2, on the `openai` package under T1 already existing. F-003-T3 and F-003-T4 are per-provider refinements layered on top of T1/T2 and are independent of each other.

## Definition of done

- Cited test(s) pass under `make test-core PROVIDER=<name>` (see AGENTS.md Testing section — this is the canonical target, not bare `go test ./core/providers/<provider>/...`, which skips the `llmtests` scenario suite).
- Converter functions remain pure (AGENTS.md's stated rule) — no HTTP calls, no logging, no side effects inside `To<Provider><Feature>Request`/`ToBifrost<Feature>Response`.

## OPEN

OPEN: is there a tracked backlog of providers planned but not yet implemented, or is "add provider" purely reactive to user requests? Not recoverable from `core/providers/` — the 30 existing packages are the full record of what exists, not of what's planned.
