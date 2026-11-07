# Aether Pulse (`aether-pulse`)

![Aether Pulse Verified Badge](./aether_pulse_badge.svg)
[![Sponsor Eloquent](https://img.shields.io/badge/Sponsor-@mjeanhudson--dev-ea4aaa?style=flat&logo=github-sponsors)](https://github.com/sponsors/mjeanhudson-dev)
[![Live Dashboard](https://img.shields.io/badge/Dashboard-Live-0066CC?style=flat)](https://mjeanhudson-dev.github.io/aether-pulse/)
[![npm package](https://img.shields.io/npm/v/aether-pulse?color=CB3837)](https://www.npmjs.com/package/aether-pulse)

**The Open-Source, "Plop-In" AI Token Efficiency Leaderboard, Cache Doctor MCP Server, & Architect Loadout Platform for Claude Code, Google Antigravity (Gemini), and OpenAI Codex CLI — Authored by Eloquent (`@mjeanhudson-dev`).**

---

## Why Aether Pulse Exists

Existing token trackers get the incentives backwards:
- **Tokscale** is a terminal/raw-volume counter that ignores multi-harness prompt-cache architecture.
- **Viberank** ranks users by **raw API dollars burned (`totalCost`)**—rewarding uncached context bloat and `while true` token farming over engineering discipline.

**Aether Pulse flips the game from *Who Burned the Most Money* to *Who Extracted the Highest Engineering Leverage Per Dollar*.**

---

## Core Architecture (The 5 Pillars)

### 1. The 3-Pillar "Leverage Index" & Weight Classes
Instead of ranking by raw spend, Aether Pulse computes a composite **Leverage Index**:
- **Pillar 1 — Cache Mastery ($\eta_{\text{cache}}$):** Rewards `90%+` Cache Hit Rates and high Cache-Write-to-Cache-Read Reuse Multipliers (`CR / CW`, e.g. `19.6x–96.7x`).
- **Pillar 2 — Multi-Model Routing Discipline:** Grants up to a **`1.24x` multiplier** when operators route high-iteration recon loops through fast models (*Gemini 3.8 Flash*, *Claude Haiku*) and reserve frontier reasoning (*Claude Opus 5.5*, *Gemini 4 Argon*, *OpenAI GPT-6.1 Sol*) for synthesis and formal verification.
- **Pillar 3 — Weight Classes:** Fair competition across budget tiers:
  - 🪶 **Featherweight (`<100M` tokens):** `$20/mo` Pro subscribers
  - 🥊 **Cruiserweight (`100M–1B` tokens):** Daily full-stack power users
  - 🏆 **Heavyweight (`1B+` tokens):** Autonomous multi-harness swarm architects

### 2. `$0/mo` Zero-Trust Open-Source Cloud Stack
- **Edge Backend:** Cloudflare Pages + Workers ([`cloud/worker.ts`](./cloud/worker.ts)) + Cloudflare D1 SQLite ([`cloud/schema.sql`](./cloud/schema.sql)) running entirely within the `$0/mo` free tier (`100,000` req/day, `5M` D1 reads/day).
- **Public Audit Ledger:** Nightly GitHub Action ([`.github/workflows/nightly-ledger.yml`](./.github/workflows/nightly-ledger.yml)) commits signed leaderboard snapshots directly to Git.

### 3. Dual-Mode "Plop-In" Integration (Hooks + MCP + 4-Tab Web UI)
- **Live Statusline & Lifecycle Hooks:** Automatically updates `~/.aether_pulse_state.json` on `SessionEnd` (Claude Code & Antigravity) and `notify` (Codex CLI).
- **Universal MCP Server ([`aether_pulse_mcp.py`](./aether_pulse_mcp.py)):** Ask your agent directly inside any harness:
  - `get_my_efficiency_rank`
  - `diagnose_cache_leaks`
  - `compare_with_cohort`
  - `export_loadout_blueprint`
- **4-Tab Interactive Dashboard ([`aether_pulse_leaderboard.html`](./aether_pulse_leaderboard.html)):** Includes Weight-Class Leaderboard, Friend/Cohort Head-to-Head Arena, Cache Doctor Diagnostics, and Architect of the Month Spotlight.

### 4. Anti-Cheat & Anti-Slop Proof-of-Work
- **Shannon Turn-Delta Entropy:** Computes Shannon entropy $H(X) = -\sum P(x)\log_2 P(x)$ over quantized turn token deltas. Synthetic `while true` loops score `< 3.5 bits` and receive automatic synthetic loop penalties; real engineering sessions score `4.0+ bits` (`VERIFIED_ORGANIC_ARCHITECT`).
- **Zero-Knowledge Git Velocity Proof:** Counts local repository commit velocity and hashes `HEAD` revisions without exposing code or commit messages.
- **Cryptographic Proof-of-Burn:** SHA-256 hash chain over every local session's token tuples.

### 5. Architect of the Month Spotlight & 1-Click Loadout Exporter
- Exports secret-scrubbed [`aether_loadout_blueprint.json`](./aether_loadout_blueprint.json) and [`AETHER_LOADOUT.md`](./AETHER_LOADOUT.md) so peers can clone top routing strategies with `python install_aether_pulse.py --apply-loadout @mjeanhudson-dev`.

---

## 💖 Sponsoring & Supporting Aether Pulse

Aether Pulse is an independent, zero-trust open-source initiative authored by **Eloquent** (`@mjeanhudson-dev`) advancing prompt-cache economics, multi-harness telemetry, and zero-tamper tactile hardware integration.

### Official Sponsorship Channels:
- **GitHub Sponsors (0% Fee):** [github.com/sponsors/mjeanhudson-dev](https://github.com/sponsors/mjeanhudson-dev)
- **Web3 / Crypto Grants:**
  - **Ethereum / Base / Arbitrum (USDC & ETH):** `0x71C808E1e3A4cDb85903c58A8b7cEa25316B386e`
  - **Solana (USDC & SOL):** `7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU`

### Patron Tiers & Accolades:
- **☕ Coffee Supporter ($5/mo):** Supporter badge in Discord & GitHub Hall of Fame.
- **⚡ Cache Patron ($25/mo):** Priority telemetry indexing & custom verified badge.
- **🏛️ Trinity Architect ($100/mo):** Co-sponsor community bounties and architecture advisory.

---

## Quickstart

```powershell
# 1. Run the multi-harness engine & generate all artifacts
python aether_pulse.py

# 2. Verify the MCP server tools
python aether_pulse_mcp.py --self-test

# 3. Run the automated test suite
python -m unittest discover -s tests -v
```
