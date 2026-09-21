---
title: How to Observe — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# How to Observe — BifrostCore

> What the system emits and how to answer questions with it.

## Signals

D: survey found no telemetry library scoped to `core/` [D: survey "Ops" — "telemetry libraries: none found"]. I: `core/` exposes a `Tracer` interface as an extension point (small pointer stored on `BifrostContext`) — basis: AGENTS.md names it as the access path for plugins/providers to reach managers without putting bulk data on context; not independently re-derived from a `core/schemas/*.go` line citation in this pass. Actual emission (Prometheus, OTel) lives in `plugins/telemetry/` and `plugins/otel/`, outside this reversed scope.

## Required instrumentation

OPEN: no log format or redaction rule is stated inside `core/` itself. The one redaction-adjacent rule that IS in evidence: no provider API key value may ever be logged or documented (survey "Configuration keys" — every secret-shaped var flagged).

## Dashboards and alerts

OPEN — not applicable to `core/` in isolation; belongs to whatever operates `transports/bifrost-http` in production.

## Debug playbook

I: for the two highest bug-fix-count files in the repo (`core/providers/bedrock/responses.go`, `core/providers/anthropic/responses.go` per the repowise health index) — first check the response-shape converter against the provider's current API docs, since that's where fixes have concentrated historically. OPEN: a general symptom→signal→runbook path — not recorded in code.
