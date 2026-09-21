---
title: Domain — Core Engine
id: DOM-001
kind: domain
feature: F-001
status: draft
owner: TBD
updated: 2026-09-21
---

# Domain — Core Engine

> Business rules, process and user flow for this domain, in the language of the business.

> Scope note: despite the `feature: F-001` frontmatter field (an artifact of which feature seeded this file at scaffold time), this is the ONE domain document for the whole `core/` module — its vocabulary and rules span F-001 (core engine), F-002 (provider abstraction), F-003 (provider implementations) and F-004 (MCP integration). Per-feature architecture and PRD documents cite back into this one.

## Ubiquitous language

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| Request | A `BifrostRequest`/`BifrostChatRequest` — a call into the engine for one of 30+ operation types (chat, embedding, speech, image, batch, file, container, …) [D: core/schemas/bifrost.go:571, core/schemas/chatcompletions.go:14, core/schemas/provider.go:681] | "call", "op" |
| Provider | An external LLM/voice/image backend behind the `Provider` interface — 20+ implementations, each covering some subset of 30+ methods [D: core/schemas/provider.go:681; survey module layout — `providers` 543 files] | "backend", "vendor" (code says provider) |
| Fallback | A named next-provider/model pair a request retries against on failure [D: core/schemas/bifrost.go:553 `type Fallback struct`] | "retry target" |
| ChannelMessage | The pooled, per-request unit that travels through the provider's queue/worker channel [D: exclusivity behavior pinned by `abandonedstream_test.go:443`] | — |
| BifrostContext | The custom, mutable `context.Context` carrying request-scoped keys (governance IDs, retry counts, trace/span, virtual key) [D: core/schemas/context.go:77] | "ctx" alone is fine in code, not in domain prose |
| Tool | An MCP-exposed function a model can call; carries `Annotations` for destructive/idempotent hints [D: core/schemas/chatcompletions.go:390 `MCPToolAnnotations`; enforcement in `mcp/auth_retry_test.go:846`] | "function" (reserved for `ChatToolFunction`, a narrower type) |
| Reasoning tokens | The subset of output/completion tokens spent on extended thinking; invariant `ReasoningTokens <= CompletionTokens` [D: core/providers/anthropic/chat.go:1357] | — |

## Actors

- I: the request-issuing caller — basis: every entrypoint into `core/` takes a `*BifrostContext` and a request struct, but `core/` defines no auth/session boundary of its own (no HTTP surface: survey "HTTP surface: none found") — the actual identity check happens upstream, in `transports/` or `plugins/governance`, outside this module.
- The provider's own API, as an external system `core/` calls out to (fasthttp/net-http client) [D: core/network/http.go:449 — proxy/CONNECT handling].
- MCP tool servers/clients, reached through `core/mcp/clientmanager.go` [D: core/mcp/clientmanager.go:2090].
- OPEN: which human role (platform engineer, application developer) is the actual consumer of the Go API `core/` exposes — not stated in code.

## Business rules

Promoted from the survey's stated-constraints, each cited to both the comment and the code/test that enforces it.

1. **DOM-001-R1** — A physical HTTP 4xx (request-bound), a 2xx, or a transient-server 5xx (including 529) on a key must not trigger key rotation; an overloaded upstream is not attributed to the key. [D: core/bifrost_test.go:804]
2. **DOM-001-R2** — Once `encrypted_content` has been stripped from a retried request, the fail-soft strip-and-retry may fire at most once per request; an upstream that keeps rejecting cannot loop. [D: core/bifrost.go:6255]
3. **DOM-001-R3** — A request-signing failure (credential problem) must not be treated as an encrypted-content validation failure; stripping `encrypted_content` cannot fix a bad signature, so no retry is attempted for that error shape. [D: core/internal/llmtests or core/encryptedreasoning_test.go:852]
4. **DOM-001-R4** — An ordinary 400 (invalid_request_error/validation_error) that carries no encrypted-content signal must not consume a retry — there is nothing the strip can fix. [D: core/encryptedreasoning_test.go:522]
5. **DOM-001-R5** — A destructive AND non-idempotent MCP tool must never be auto-retried on an auth-shaped failure; the original error surfaces unchanged. A destructive-but-idempotent tool, and a tool with no annotations at all (fail-closed: treated as destructive+non-idempotent), follow the same skip rule; only destructive-and-idempotent tools are retried. [D: core/mcp/auth_retry_test.go:811, :846, :875]
6. **DOM-001-R6** — `ValidateMCPClientName`: MCP client names must be ASCII-only, contain no spaces or hyphens, and must not start with a digit. [D: core/mcp/utils.go:857]
7. **DOM-001-R7** — CONTRADICTED, not confirmed: the comment at `core/mcp/clientmanager.go:2090` claims a new client entry "Initialize[s] State to Disconnected... transitions to Connected only on success," but the code on that line sets `State: schemas.MCPConnectionStateUnstable`, and neither `Disconnected` nor `Connected` exist anywhere in the real `MCPConnectionState` enum (actual values: `healthy`, `unstable`, `error`, `pending_verification`, `disabled`, `needs_reauth`, `degraded` — see `ddd/domain_DOM-001-mcp-integration.md`'s Open questions for the full citation). The rule as stated is not enforceable because its named states don't exist; do not treat this as a confirmed invariant until reconciled with the real enum.
8. **DOM-001-R8** — An operation driven by an input asset (video upscale, image-to-3D) must carry no prompt; the provider rejects the combination if one is supplied, because the model cannot serve it. [D: core/bifrost.go:1951]
9. **DOM-001-R9** — Extended-thinking (reasoning) token count is always a subset of output tokens: `ReasoningTokens <= CompletionTokens` must hold; no folding/adjustment is performed to enforce it separately. [D: core/providers/anthropic/chat.go:1357]
10. **DOM-001-R10** — A `ChannelMessage`'s claim/abandon state machine is exclusive: exactly one side (worker vs. abandon-timeout path) wins a given message, and a fresh message drawn from the pool always starts in the open (unclaimed) state. [D: core/abandonedstream_test.go:443]

I: R1–R4 and R2's retry-budget logic together describe one coherent "fail-soft-once" policy for encrypted-reasoning content across the whole request-retry path — basis: all four are asserted in the same test file family (`bifrost_test.go`, `encryptedreasoning_test.go`) and reference the same `bifrost.go:6255` strip site.

## Process flow

D: happy path, from `core/bifrost.go`'s request lifecycle and `core/inference.go`'s routing (per AGENTS.md's Request Flow section, itself derived from these same files — not re-cited per line here since AGENTS.md already names `core/bifrost.go` and `core/inference.go` as its source):
1. Request enters via a Go call (chat/responses/embedding/... per `Provider` interface method) [D: core/schemas/provider.go:681].
2. Routed to the provider's per-provider queue/worker channel as a pooled `ChannelMessage` [D: core/abandonedstream_test.go:443].
3. Provider call executes; on failure, fallback/rotation rules (R1) decide whether to rotate keys or fall through to a `Fallback` [D: core/schemas/bifrost.go:553].
4. Response returned, or streamed as `BifrostStreamChunk` [D: core/schemas/bifrost.go:1913].

Alternate/error paths: encrypted-content fail-soft-once retry (R2–R4); MCP auth-failure retry gated by tool destructiveness/idempotency (R5).

OPEN: the full state diagram for `ChannelMessage` (claimed/abandoned/released) beyond the one exclusivity invariant a test name states.

## Invariants

- `ReasoningTokens <= CompletionTokens` at all times (R9).
- A `ChannelMessage` claim is exclusive — never double-claimed (R10).
- Rotation never fires on a request-bound 4xx, a 2xx, or a transient 5xx/529 (R1).
- The encrypted-content strip-and-retry fires at most once per request (R2).

## Implementation status

| Rule | Status | Evidence |
| --- | --- | --- |
| DOM-001-R1 | wip — unverified, run `go test ./... -run TestExecuteRequestWithRetries` in `core/` (per AGENTS.md, `make test-core` is the canonical entrypoint but hits live provider APIs — not run here) | `core/bifrost_test.go:804` names the case |
| DOM-001-R2 | wip — unverified, run `go test ./... -run TestExecuteRequestWithRetries_NoStripWhenNothingEncrypted` in `core/` | `core/encryptedreasoning_test.go:522` |
| DOM-001-R3 | wip — unverified, run `go test ./...` in `core/`, matching `TestMantleEncryptedContentRefusalIsNotConfusedWithOtherValidationErrors` | `core/encryptedreasoning_test.go:1237` |
| DOM-001-R4 | wip — unverified, same command as R2 | `core/encryptedreasoning_test.go:522` |
| DOM-001-R5 | wip — unverified, run `go test ./mcp/... -run TestExecuteTool_AuthFailureRetry` | `core/mcp/auth_retry_test.go:689,811,846,875` |
| DOM-001-R6 | wip — unverified, run `go test ./mcp/...` matching `ValidateMCPClientName` | `core/mcp/utils.go:857` (function under test; test file not separately named in survey) |
| DOM-001-R7 | wip — unverified, no dedicated test name surfaced in survey | `core/mcp/clientmanager.go:2090` (comment only) |
| DOM-001-R8 | wip — unverified, no dedicated test name surfaced in survey | `core/bifrost.go:1951` (comment only) |
| DOM-001-R9 | wip — unverified, no dedicated test name surfaced in survey beyond the comment | `core/providers/anthropic/chat.go:1357` |
| DOM-001-R10 | wip — unverified, run `go test ./... -run TestChannelMessageHandoffIsExclusive` in `core/` | `core/abandonedstream_test.go:443` |

None of these were run in this session (see project-management/BifrostCore charter's constraints and the testing_strategy.md rationale for not running `core/`'s live-API test suite unattended).

## Open questions

- OPEN: DOM-001-R8 is a comment-only claim with no test name found in the survey's cited evidence — is the invariant actually enforced anywhere, or only documented in a comment next to code that could drift from it? DOM-001-R7 is worse than unverified: it is actively contradicted by the code it cites (see above) — flag to the code owner as a stale/wrong comment, not merely an untested rule.
- OPEN: what business rule, if any, governs *which* fallback is chosen first when several are configured — `Fallback` (bifrost.go:553) defines the shape but not a selection policy in the cited evidence.
- OPEN: is there a domain rule for MCP tool filtering beyond the four-level hierarchy AGENTS.md names (global/client/tool/per-request) — the interaction rule when levels disagree is asserted in AGENTS.md prose, not pinned to a specific test in this survey.
