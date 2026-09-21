---
title: Resource & Cost Estimate — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Resource & Cost Estimate — BifrostCore

> Rough order-of-magnitude people, infrastructure and licence cost.

## Team shape

OPEN: role allocation is an organisational fact. The nearest code-derived proxy is ownership concentration: repowise reports 3 contributors own >60% of the whole repo's files by commit history (30.5% + 19.2% + 10.4%) [D: repowise get_overview `knowledge_map.top_owners`] — this describes historical contribution share, not a staffing plan.

## Infrastructure and services

`core/` itself provisions no infrastructure — D: survey found no containers, CI config, deploy config or telemetry libraries scoped to `core/` [D: survey "Ops" section — "containers: none / ci: none / deploy: none / telemetry libraries: none found"]. It is a library; infra decisions live in `transports/`, `plugins/telemetry/`, and `terraform/`, outside this reversed scope.
OPEN: monthly cost and scaling triggers — not expressed anywhere in `core/`.

## Estimate confidence

OPEN: no cost or resource estimate exists in code to have a confidence range on.
