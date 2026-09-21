---
title: Stakeholder Analysis — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Stakeholder Analysis — BifrostCore

> Identify who decides, who is consulted and who is only informed.

## Stakeholder map

I: the repository's top code owners by files-owned are the closest recoverable proxy for stakeholders — basis: repowise's knowledge map over the full repo (not `core/`-scoped) lists Akshay Deo (30.5%), Pratham Mishra (19.2%), Suresh Chaudhary (10.4%) as top owners by files-owned [D: repowise get_overview `knowledge_map.top_owners`]. This is an ownership signal, not a stated stakeholder role — OPEN: their actual roles (maintainer, reviewer, sponsor) are not recorded in code.
OPEN: everyone else — interest, influence, engagement strategy are organisational facts, not code facts.

## Decision rights

OPEN: not recoverable from code. `core/`'s own bus-factor is thin — repowise reports 1,511 of the repo's files have a bus factor of 1 (avg 1.8) [D: repowise get_overview `git_health.avg_bus_factor: 1.8`, `files_with_bus_factor_1: 1511`], which is a risk signal, not a decision-rights record.

## Communication cadence

OPEN: no ceremony, meeting cadence or communication artifact is recorded in `core/`. The only recurring artifact the code produces is `core/changelog.md` [D: survey "In-repo documents"], which is a release record, not a communication cadence.
