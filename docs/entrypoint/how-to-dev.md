---
title: How to Develop — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# How to Develop — BifrostCore

> The development loop for a human or agent, from picking a task to opening a PR.

## Before you start

Read `docs/BifrostCore-Specs/route/route_1.9.1_F-<nnn>.md` for the feature you're touching, then confirm the task exists in `tasks/tasks_1.9.1_F-<nnn>.md` — do not start work with no corresponding task row.

## Loop

1. Pick a `todo` task from `tasks/tasks_1.9.1_F-<nnn>.md`.
2. Read that feature's route file, domain doc (`ddd/domain_DOM-001-core-engine.md`, shared), and architecture doc (`architect/feature_1.9.1_F-<nnn>_architect.md`).
3. Implement in `core/` per the module scope: F-001 → `bifrost.go`/`inference.go`/`network/`; F-002 → `schemas/`; F-003 → `providers/`; F-004 → `mcp/`.
4. Self-check against `architect_common.md`'s Review checklist.
5. Move the task to `wip` (and `done` once its test passes here) via `docs_flow.py task`, then open the PR.

## Standards

See `architect/architect_common.md` — not restated here.

## Definition of done

I: assembled from `status-model.md`'s "What done costs" section (not `core/`-specific): a task is `done` only when its done-when check passed in this environment, with the command/result in the note — "the code looks finished" is `wip`, never `done`.
