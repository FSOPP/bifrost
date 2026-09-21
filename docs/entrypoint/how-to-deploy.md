---
title: How to Deploy — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# How to Deploy — BifrostCore

> The deployment procedure and its guardrails.

`core/` is not independently deployed — see `deployment/deployment_strategy.md` for why (it's a library, not a service). This file exists as the standard entrypoint but its content is `OPEN` at the `core/` level.

## Preconditions

OPEN — not applicable to `core/` in isolation; deployment gates belong to `transports/bifrost-http` or `cli/`, which are out of this reversed scope.

## Procedure

OPEN — see above.

## Verification

OPEN — see above.

## Rollback

OPEN — see above.
