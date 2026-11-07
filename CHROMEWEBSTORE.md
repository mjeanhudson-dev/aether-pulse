# Chrome Web Store Listing — Aether Pulse — AI Harness Liquid Telemetry Overlay

> Last Updated: 2026-11-06

## Store Listing

**Extension Name**
Aether Pulse — AI Harness Liquid Telemetry Overlay

**Short Description**
Draggable liquid-physics telemetry overlay for Claude Code, Google Antigravity, and OpenAI Codex CLI with 1-click harness switching.

**Detailed Description**
Track your AI coding efficiency, prompt-cache hit rate, and retail compute savings in real time across Anthropic Claude Code, Google Antigravity, and OpenAI Codex CLI.

Key Features:
Draggable Liquid-Physics HUD: Moves with natural weight and fluid meniscus feedback whose level reflects your live Prompt-Cache Hit percentage.
Automatic Harness Detection: Senses which AI workspace you are actively using as you drag the overlay across browser tabs or developer dashboards.
One-Button Side Switcher: Click the side toggle button on the overlay to switch between Auto-Sense Target, All 3 Harnesses side-by-side comparison, or a pinned single harness.
Cupertino Light & Dark Telemetry: High-contrast tabular numerals designed for zero visual fatigue during long coding sessions.

**Category**
Developer Tools

**Single Purpose**
Displays a draggable real-time AI token efficiency and prompt-cache telemetry overlay across developer and AI coding web workspaces.

**Primary Language**
English

## Graphics & Assets

| Asset | Dimensions | Status | Filename |
|-------|-----------|--------|----------|
| Store Icon | 128×128 PNG | ✅ Ready | `chrome-extension/icons/icon-128.png` |
| Toolbar Icon (48) | 48×48 PNG | ✅ Ready | `chrome-extension/icons/icon-48.png` |
| Toolbar Icon (16) | 16×16 PNG | ✅ Ready | `chrome-extension/icons/icon-16.png` |
| Screenshot 1 | 1280×800 | ✅ Ready | `aether_pulse_leaderboard.html` |

## Permissions Justification

| Permission | Type | Justification |
|------------|------|---------------|
| `storage` | permissions | Saves the user's selected overlay display mode (`Auto-Sense`, `All 3 Harnesses`, or pinned harness) locally across browser sessions. |
| `tabs` | permissions | Identifies which AI coding workspace domain is open in the active tab so the overlay automatically displays the matching harness metrics. |
| `alarms` | permissions | Periodically refreshes local token efficiency metrics in the background without keeping the service worker persistently awake. |
| `http://127.0.0.1:8765/*` | host_permissions | Connects to the user's local Aether Pulse telemetry daemon on localhost to stream real-time multi-harness token and cache statistics. |
| `https://mjeanhudson-dev.github.io/*` | host_permissions | Synchronizes verified leaderboard and badge telemetry on the public Aether Pulse dashboard. |

## Privacy & Data Use

### Data Collection
**Does the extension collect user data?** No

### Data Use Certification
- [x] Data is NOT sold to third parties
- [x] Data is NOT used for purposes unrelated to the extension's core functionality
- [x] Data is NOT used for creditworthiness or lending purposes

## Privacy Policy
**Privacy Policy URL**: https://github.com/mjeanhudson-dev/aether-pulse/blob/main/PRODUCT.md

## Distribution
**Visibility**: Public
**Regions**: All regions

## Developer Info
**Publisher Name**: Eloquent (`@mjeanhudson-dev`)
**Contact Email**: mjeanhudson@gmail.com
**Support URL / Email**: https://github.com/mjeanhudson-dev/aether-pulse/issues
**Homepage URL**: https://mjeanhudson-dev.github.io/aether-pulse/

## Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| 1.0.0 | 2026-11-06 | Initial Cupertino Telemetry release with weighty liquid-physics draggable HUD and 1-button harness switcher. | Ready |
