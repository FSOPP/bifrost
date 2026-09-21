---
title: Master Task Index — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Master Task Index — BifrostCore

> Index of task files with status roll-up. Not a substitute for the tracker.

## Task files

| Version | Feature ID | Link | Status | Blocked-by |
| --- | --- | --- | --- | --- |
| 1.9.1 | F-001 | `tasks/tasks_1.9.1_F-001.md` | wip — unverified (see file) | — |
| 1.9.1 | F-002 | `tasks/tasks_1.9.1_F-002.md` | wip — unverified (see file) | — |
| 1.9.1 | F-003 | `tasks/tasks_1.9.1_F-003.md` | wip — unverified (see file) | — |
| 1.9.1 | F-004 | `tasks/tasks_1.9.1_F-004.md` | wip — unverified (see file) | — |

All four are as-built inventories of already-shipped code (`core/` is at version `1.9.1` [D: core/version:1]), not a forward plan — see `filling.md`'s "Tests and tasks" section: these documents invert their usual meaning.

## Conventions

Task ID format: `F-nnn-T{n}` (e.g. `F-001-T3`). Status vocabulary and the `done`-cost rule are defined once in `status-model.md` — not restated here. Every `done-when` in a per-feature task file is written as the check that *would* prove the task, per `filling.md`: "Write the `done-when` as the check that would prove it, because that is what the status column then has to cash." No task in this reversed hub is marked `done` without the corresponding `go test` command having been run in this session — none was (see `testing_strategy.md` for why).

OPEN: is there an organisational tracker (Linear, Jira, GitHub Projects) that already holds a forward-looking task backlog for `core/`, separate from this as-built inventory? Not discoverable from the code.
