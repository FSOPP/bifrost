---
title: Data Model 1.9.1 F-003 — Provider Implementations
id: F-003
status: draft
owner: TBD
updated: 2026-09-21
---

# Data Model 1.9.1 F-003 — Provider Implementations

> The slice of the data model this feature reads and writes, at field precision.

## Scope

This feature owns no persisted entity and there is no database anywhere in `core/` — [D: reverse.py survey, core/, 1 entity found total across the whole module, `confidence: low`, fields not extractable — `core/providers/gemini/types.go:1345`]. What `core/providers/` actually defines is a large set of **transient, in-memory wire structs** — one request and one response type per provider per operation, used only for JSON marshaling to/from the third-party API and discarded after the call. These are not domain entities in the ERD/schema.json sense this template assumes, so this document does not add rows to `schemas.json` (out of scope for this feature's files) or invent a plausible entity shape to satisfy the template.

Read: the shared Bifrost wire types owned by F-002 (`schemas.BifrostChatRequest`, `schemas.BifrostChatResponse`, etc.). Write: nothing persisted. Own: the provider-specific wire structs, e.g. `AnthropicMessageRequest`/`AnthropicMessageResponse` [D: core/providers/anthropic/chat.go:339,1131], `BedrockConverseRequest`/`BedrockConverseResponse` [D: core/providers/bedrock/chat.go:14,91] — these are scoped to this document but not promoted to `schemas.json`.

## Feature ERD

`schema/erd_1.9.1_F-003.puml` is intentionally left with no entities — see Scope above. It is not a stub oversight; it is the honest answer for a stateless converter layer.

## Field definitions

N/A — no persisted fields. The provider-specific wire structs' fields are documented as citations in `architect/feature_1.9.1_F-003_architect.md`'s Sequence section rather than duplicated here as a fake schema table.

## New and changed entities

None added to `data-master-erd.md` by this feature.

## Migrations

None — no database.

## Traceability

N/A.

## OPEN

OPEN: should the provider-specific wire structs (30 packages × ~2-10 request/response types each) be captured in `schemas.json` anyway, purely as a documented type inventory (not because they're persisted), so a future agent adding a 31st provider has a catalogue of the existing shapes to follow? The scaffold's data layer is built for persisted entities, and stretching it to catalogue transient DTOs is a judgment call this document defers rather than makes unilaterally.
