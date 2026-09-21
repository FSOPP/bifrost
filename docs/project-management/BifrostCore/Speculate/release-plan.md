---
title: Release Plan — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Release Plan — BifrostCore

> Map features to release windows. Adaptive: windows, not fixed dates.

## Releases

D: the only recorded release identity for `core/` is its own version file, currently `1.9.1` [D: core/version:1]. `core/changelog.md` is the as-shipped release record [D: survey "In-repo documents"].

| Version | Theme | Included feature IDs | Target window | Exit criteria |
| --- | --- | --- | --- | --- |
| 1.9.1 (current) | I: provider-shape and streaming fixes — basis: `core/changelog.md` and the repo's most-recent commits (`fix: mint Bifrost-issued ephemeral tokens...`, `handle empty reasoning chunks`, `fixes abandoned connection handling...`) all land in F-001/F-003 scope | F-001, F-002, F-003, F-004 (all, current state) | OPEN | OPEN |

## Iteration cadence

OPEN: no sprint length, review or retro rhythm is recorded in code.

## Assumptions

OPEN: capacity and velocity are team facts, not code facts. The repo's commit history is high-frequency (7,154 commits total, 34 contributors [D: survey "History"]) but that describes past throughput, not a capacity assumption for future planning.
