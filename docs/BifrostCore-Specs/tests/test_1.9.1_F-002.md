---
title: Test Plan 1.9.1 F-002 — Provider Abstraction
id: F-002
kind: test
feature: F-002
version: 1.9.1
status: draft
owner: TBD
updated: 2026-09-21
---

# Test Plan 1.9.1 F-002 — Provider Abstraction

> Concrete cases traced back to acceptance criteria.

> This package's tests were built before this document — as with every reversed test plan, "coverage" here means what already exists, and the point of the document is to name the holes, not to claim completeness.

`core/schemas` has 55 `_test.go` files totalling roughly 490 top-level `Test*` functions (many table-driven with further subtests) [D: `for f in *_test.go; do grep -c '^func Test' $f; done` over `core/schemas/`]. Cataloguing every subtest individually is out of this document's practical scope; cases below are grouped by file/theme, one `F-002-TC<k>` per theme, each citing its file and a representative test name.

## Traceability matrix

| Story | Test cases | Level |
| --- | --- | --- |
| F-002-US1 (interface stability) | F-002-TC1 | unit |
| F-002-US2 (optional-interface capability detection) | F-002-TC2 | unit |
| F-002-US3 (context reserved-key guard) | F-002-TC3, F-002-TC4 | unit |
| F-002-US4 (plugin pipeline symmetry / config marshaling) | F-002-TC5, F-002-TC6 | unit |

## Test cases

- **F-002-TC1** — Model-capability fallback resolution. Preconditions: a `ModelCapabilities` row absent or silent for a (provider, model) pair. Steps: call the capability lookup. Expected: caller-supplied fallback is used without erroring. [D: modelcapabilities_test.go — `AbsentFallsBack:188`, `AbsentRowFallsBack:215`, `CallerFallbackUsedWhenRowIsSilent:327,357`]
- **F-002-TC2** — Context grant precedence and inheritance across `BifrostContext.Root()`/scoped contexts. [D: context_grant_test.go, 6 test functions]
- **F-002-TC3** — `BifrostContext` core behaviour: deadline propagation, `SetValue`/`Value` thread-safety, plugin scoping. [D: context_test.go, 18 test functions]
- **F-002-TC4** — `fasthttp.RequestCtx` interop — never reading through a pooled, non-cancelling parent. [D: context_fasthttp_test.go, 2 test functions]
- **F-002-TC5** — `Plugin` interface conformance / config marshaling round trip. [D: plugin_test.go, 3 test functions]
- **F-002-TC6** — General schema (de)serialization round trips (JSON native types, ordered maps, tool-choice marshaling, redaction). [D: serialization_test.go (52 funcs), orderedmap_test.go (34), redaction_test.go (9), toolchoicemarshal_test.go (6)]

## Implementation status

| Test case | Status | Evidence |
| --- | --- | --- |
| F-002-TC1 | wip — unverified, run `go test ./core/schemas/... -run TestModelCapabilities` | not run in this pass (see report: test-execution declined pending live-API cost review) |
| F-002-TC2 | wip — unverified, run `go test ./core/schemas/... -run TestContextGrant` | not run |
| F-002-TC3 | wip — unverified, run `go test ./core/schemas/... -run TestBifrostContext` | not run |
| F-002-TC4 | wip — unverified, run `go test ./core/schemas/...` (file has no shared `Test` prefix beyond individual func names) | not run |
| F-002-TC5 | wip — unverified, run `go test ./core/schemas/...` | not run |
| F-002-TC6 | wip — unverified, run `go test ./core/schemas/...` | not run |

## Edge and negative cases

`NetworkConfig.UnmarshalJSON` rejecting a malformed duration string [D: core/schemas/provider.go:163-166]; `AllowedRequests.IsOperationAllowed` defaulting to `false` for an unknown `RequestType` (fail-closed) vs. a nil `*AllowedRequests` defaulting to `true` (fail-open) [D: core/schemas/provider.go:401-404, 529-531 — AGENTS.md gotcha #10]; `SetValue` on a reserved key while `blockRestrictedWrites` is set silently drops the write rather than erroring [D: core/schemas/context.go:480-484].

## Out of scope

Provider-specific test suites (`core/providers/*/*_test.go`) — covered under F-003. MCP protocol tests (`core/mcp/*_test.go`) — covered under F-004. 

OPEN: whether any of the 490 test functions in this package require live provider credentials (none appeared to on inspection, but the full file set was not individually executed to confirm).
