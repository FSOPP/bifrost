#!/usr/bin/env python3
"""Rule config for 1.9.1 F-004.

Config only — the logic lives in route.py. Add paths to EXTRA as the feature's
document set grows, then re-run this file to regenerate the JSON.

    python rule_1.9.1_F-004.py
"""
from route import build, emit

VERSION = "1.9.1"
FEATURE_ID = "F-004"
FEATURE_TITLE = "MCP Integration"

EXTRA = {
    "domain": ["docs/BifrostCore-Specs/ddd/domain_DOM-001-mcp-integration.md"],
    "adrs": ["docs/BifrostCore-Specs/ADRs/adrs_ADR-0001-record-architecture-decisions.md"],
    "runbooks": ["docs/BifrostCore-Specs/runbook/runbook_DEV_RB-001-local-setup.md"],
    "tests": ["docs/BifrostCore-Specs/tests/test_1.9.1_F-004.md"],
}

if __name__ == "__main__":
    emit(build(VERSION, FEATURE_ID, FEATURE_TITLE, EXTRA))
