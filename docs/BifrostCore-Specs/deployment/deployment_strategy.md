---
title: Deployment Strategy — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Deployment Strategy — BifrostCore

> Environments, pipeline, release mechanics and rollback.

`core/` is a Go library module with no container, CI or deploy configuration of its own — D: survey "Ops" section reports "containers: none / ci: none / deploy: none / health endpoints: none found / telemetry libraries: none found" scoped to this root [D: survey.md "Ops"]. It ships by being imported (`go.work`) and versioned via `core/version` [D: core/version:1, currently `1.9.1`], not deployed standalone. Deployment topology (containers, Helm, Terraform) lives at the repo root (`terraform/`, `helm-charts/`) and in `transports/`, outside this reversed scope.

## Environments

OPEN: not applicable at the `core/` level — no environment-specific config was found scoped to this module.

## Local development

I: the one path is the repo-level `make dev` command — basis: AGENTS.md's stated "Development: `make dev`" — not independently re-verified by running it in this pass. See `runbook/runbook_DEV_RB-001-local-setup.md` for the step list.

## Pipeline stages

OPEN: no build/test/scan/package/deploy pipeline is defined scoped to `core/` (survey: "ci: none"). Repo-level CI (`.github/workflows/`) exists per the repowise index but was not independently traced in this pass.

## Release mechanics

- D: versioning is a flat string in `core/version` [D: core/version:1] — no semver-parsing logic was inspected in this pass to confirm the scheme.
- OPEN: migration ordering — not applicable, `core/` has no migrations.
- OPEN: feature flags, rollback trigger — none found scoped to `core/`.

## Configuration and secrets

D: 40+ provider API keys are read from env vars in test files (survey "Configuration keys" — full list, secret-shaped entries flagged, e.g. `ANTHROPIC_API_KEY`). No value from any of them is recorded here, per the skill's hard rule.
OPEN: production secret delivery mechanism (vault, k8s secret, env file) — not stated inside `core/` itself; that is a `transports/`/deployment-layer concern.
