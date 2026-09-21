---
title: Research & Reference Material — BifrostCore
status: draft
owner: TBD
updated: 2026-09-21
---

# Research & Reference Material — BifrostCore

> External APIs, third-party specs and spikes, with the date each was checked.

## Third-party integrations

D: 20+ LLM/voice/image provider APIs, one Go package per provider under `core/providers/` [D: survey "Module layout" — `providers` 543 files]. Representative set with the env var each test file reads (name only, no value, per this hub's hard rule): OpenAI (`OPENAI_API_KEY`), Anthropic (`ANTHROPIC_API_KEY`), AWS Bedrock (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`), Azure (`AZURE_API_KEY`/`AZURE_ENDPOINT`), Google Vertex (`VERTEX_API_KEY`/`VERTEX_CREDENTIALS`), Gemini (`GEMINI_API_KEY`), Groq, Cerebras, Cohere, Mistral, DeepSeek, Fireworks, Databricks, ElevenLabs, HuggingFace, Nebius, OpenRouter, Parasail, Perplexity, Replicate, Runware, Runway, Sarvam, GitHub Copilot, xAI, vLLM, Ollama, SGLang [D: survey "Configuration keys" — full list]. OPEN: docs link, auth model detail and rate limits per provider — not recorded in `core/`, would need each provider's own external documentation, checked on a date this reversal did not perform.

## Spikes

OPEN: no spike record exists in `core/`. The nearest evidence of exploratory work is the git history's churn concentration in `core/providers/bedrock/responses.go` and `core/providers/anthropic/responses.go` (55 and 46 bug fixes respectively per the repowise health index) — I: this suggests iterative discovery of correct response-shape handling for these two providers, but no spike document or ADR records the question/method/finding.

## Reference material

- `core/changelog.md` — the module's own as-shipped release record [D: survey "In-repo documents"].
- AGENTS.md (repo root) — the closest thing to a living architecture reference for this whole repo, cited throughout this hub as `I:` (not `core/`-internal, so never `D:`).
