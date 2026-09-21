---
title: ADR-0001 — Record Architecture Decisions
id: ADR-0001
kind: adr
feature: F-001
status: draft
owner: TBD
updated: 2026-09-21
---

# ADR-0001 — Record Architecture Decisions

> Bootstrap ADR: establish that decisions are recorded as ADRs in this repository.

## Status

Accepted (reconstructed from reversal, 2026-09-21) — rationale not recovered; this is the hub's bootstrap ADR, not a `core/`-specific decision.

## Context

`core/` (the `github.com/maximhq/bifrost/core` module [D: core/go.mod:1]) has no in-repo ADR log prior to this reversed hub: the survey found `core/changelog.md` as the only in-repo document [D: survey "In-repo documents"], and several architecturally consequential choices are visible in code with no recorded reasoning nearby — e.g. the per-request cloned streaming `fasthttp` client [D: providers/anthropic/anthropic.go:1514] and the fail-soft-once encrypted-content strip [D: core/bifrost.go:6255].

## Decision

From this hub forward, an architecturally significant decision for `core/` is recorded as an ADR under `docs/BifrostCore-Specs/ADRs/`, following the reconstructed-ADR shape in `.claude/skills/product-reverse-docs/references/filling.md` (Status / Context / Decision / Alternatives considered / Consequences) when back-filling a decision whose original reasoning was not recorded.

## Alternatives considered

OPEN: not recoverable — code retains no record of what was rejected, and no ADR practice existed in this module before this reversal.

## Consequences

I: every reconstructed ADR for this module must state its Alternatives-considered field as `OPEN` rather than invent one — basis: `filling.md`'s explicit warning that "a reconstructed ADR that invents its own Alternatives table is worse than no ADR." OPEN: whether the team adopts this practice going forward is an organisational decision, not a code fact.

## Context

<!-- Why decision history matters for this product and its agents. -->

TBD

## Decision

<!-- What is now the rule. -->

TBD

## Alternatives considered

<!-- Table: option, why not. -->

TBD

## Consequences

<!-- Positive, negative, and what this now obliges the team to do. -->

TBD

## Links

<!-- Related domain docs, PRDs, architecture sections. -->

TBD
