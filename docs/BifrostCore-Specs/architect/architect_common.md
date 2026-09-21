---
title: Common Engineering Standards — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Common Engineering Standards — BifrostCore

> The shared rules every feature and every agent must follow.

## Tech stack

| Concern | Choice | Version | ADR reference |
| --- | --- | --- | --- |
| Language | Go | 1.27.0 (workspace-pinned) [D: core/go.mod:3] | ADR-0001 (bootstrap only — no stack-choice ADR exists) |
| Module | `github.com/maximhq/bifrost/core`, 71 declared dependencies [D: survey "Stacks" table] | — | — |
| HTTP client (providers) | `fasthttp` (unary + a cloned streaming client per request) [D: providers/anthropic/anthropic.go:1514] | I: per-provider, not centrally pinned — OPEN: exact fasthttp version | — |
| HTTP client (Bedrock) | `net/http` with `ForceAttemptHTTP2` [I: basis — AGENTS.md's stated Bedrock exception; not independently re-derived from a `providers/bedrock/*.go` citation in this pass] | OPEN | — |
| JSON | `sonic` in hot paths, `encoding/json` for custom marshaling in `schemas/`, `gjson`/`sjson` for single-field reads [I: basis — AGENTS.md gotcha #13, consistent with `providers/utils/utils.go` existing per survey module layout] | OPEN | — |

## Project layout

D: from the surveyed module layout — `providers` (543 files, largest), `schemas` (130), `internal` (117 — test infra: `llmtests` + `mcptests`), `mcp` (54), root (19 — engine), `network` (8), `keyselectors` (1) [D: survey "Module layout"].
I: import direction is one-way toward `schemas` — basis: repowise's dependency-edge counts show `core/providers -> types` (5,740 refs) and `core/internal -> types` (4,130 refs) as the two heaviest edges touching `core/`, with no edge running the other way in the reported graph [D: repowise get_overview architecture-map edges]. So: `providers/`, `mcp/`, `internal/` may import `schemas/`; `schemas/` imports none of them.

## Naming conventions

D: no filename contains an underscore except the `_test.go` suffix, and multi-word filenames concatenate lowercase (e.g. `abandonedstream_test.go`'s sibling non-test files would be `abandonedstream.go`, `encryptedreasoning.go`) [I: basis — the file list itself: `core/abandonedstream_test.go`, `core/encryptedreasoning.go`, `core/azurestreamretry_test.go` all follow this shape; no counterexample surfaced in the survey's file listing].
D: provider types are prefixed with the provider name in PascalCase, e.g. `AnthropicChatRequest`-shaped names — pattern visible in `providers/anthropic/*.go` structuring per survey module layout.
D: converter functions carry the `To<Provider><Feature>Request` / `ToBifrost<Feature>Response` shape — visible in the citation `providers/anthropic/chat.go` housing chat converters (survey "Provider Implementation" file pattern, cross-checked against `providers/anthropic/chat.go:1052,1357,1957` all being converter-site citations).

## Design patterns

- D: sync.Pool-backed object pooling with an explicit prod/debug dual build (`pool_prod.go` zero-overhead, `pool_debug.go` leak/double-release tracking) [I: basis — survey's stated constraints repeatedly reference "released...cannot pin" and pooled `ChannelMessage` semantics, e.g. `core/bifrost_test.go:3555`].
- D: pure converter functions — provider request/response transformers take no HTTP client and do no logging (pattern implied by the `To*Request`/`ToBifrost*Response` naming convention above; not independently verified line-by-line in this pass — I: mark this a convention-as-practised claim, not a compiler-enforced one).
- Rejected/avoided: mutating a shared slice in place for the providers/plugins list — I: basis — `bifrost.go`'s repeated `atomic.Pointer`-shaped comments around config reload (`bifrost.go:6918` "write all internal signals explicitly", `bifrost.go:8836`/`8897` about not leaving stale references) suggest copy-then-swap is the sanctioned pattern; OPEN whether this is enforced anywhere beyond convention.

## Code quality

D: 4385 test cases across 454 test files in `core/` [D: survey "Tests" — "files: 454, cases: 4385"], declared entrypoint `go test ./...` [D: core/go.mod:1, survey "Tests" "declared command"].
OPEN: no lint config, no complexity/size limit, no formatter config was found scoped to `core/` in this survey (repo-wide `make lint`/`make fmt` exist per AGENTS.md but were not independently re-verified against `core/` in this pass).

## Security baseline

D: 47 distinct provider API-key-shaped env vars are read across `core/providers/*_test.go` (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `AWS_SECRET_ACCESS_KEY`) [D: survey "Configuration keys" — full list, secret-shaped entries flagged]. None of these values are recorded anywhere in this hub, by the skill's own rule.
D: `network/http.go` implements CONNECT-based HTTPS-through-HTTP-proxy tunneling with proxy auth via `ProxyConnectHeader` [D: core/network/http.go:449].
OPEN: authz/input-validation policy beyond the one stated constraint found (MCP client name validation, `mcp/utils.go:857`) — a full security review of `core/` was not performed as part of this reversal.

## Review checklist

I: assembled from AGENTS.md's stated testing rules (not independently re-derived from `core/` code, since a checklist is a team practice, not a code fact) — OPEN whether this checklist is actually enforced in `core/`'s own PR process:
- [ ] OPEN: is a regression test added for every fix (AGENTS.md states this as a repo-wide rule; not verified against `core/`'s actual merge history in this pass)
- [ ] `go test ./...` run and green for the touched package
- [ ] Pooled objects have every field reset before `Put()` (AGENTS.md gotcha #1, applicable to `core/pool/`)
- [ ] No `.env`/secret value copied into any doc or log
