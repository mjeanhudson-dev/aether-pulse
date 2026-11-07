---
name: aether-agent-kit
description: "Production-grade autonomous AI agent skill kit for prompt-cache mastery, multi-harness token telemetry profiling, 3-lens cost accounting (Secular / Specular / Spectacular), and tactile HUD integration."
version: 1.1.0
---

# Advanced Aether Agent Skill Kit (`aether-agent-kit`)
Author: **Eloquent** (`@mjeanhudson-dev`)

The **Aether Agent Skill Kit** equips autonomous AI agents and subagent swarms (Google Antigravity, Anthropic Claude Code, OpenAI Codex CLI, Cursor, Windsurf, Continue) with production-grade prompt cache mastery, automated token accounting, and live telemetry hooks.

---

## 1. Core Agent Capabilities

1. **Prompt-Cache Prefix Optimization**:
   - Enforce static prefix immutability. System prompts, AST schemas, and project invariants must remain pinned at the head of context to preserve KV-cache hits (>92%).
   - Dynamic session variables (current timestamp, volatile diffs, scratch notes) are strictly relegated to tail turns.

2. **3-Lens Usage & Value Accounting**:
   - **💎 Specular Lens (Official Metered API Standard)**: Standard metered developer API cost (e.g. Gemini 3.8 Flash at $0.75/M in, $3.75/M out, $0.075/M cache read).
   - **👁️ Secular Lens (Earthly Cash Outlay)**: Flat out-of-pocket cash paid for monthly subscription seats ($20.00/mo flat for Google AI / Gemini Advanced).
   - **⚡ Spectacular Lens (Frontier Market Replacement Worth)**: Gross computational replacement worth if executed un-cached on frontier models ($3.00/M in, $15.00/M out). Decomposes Net Synthesized Code Yield vs. Cached Stream.

3. **Autonomous Quota Sentinel & 429 Circuit Breaker**:
   - Continuous auditing against the **10,000,000 daily token volume sentinel threshold**.
   - Immediate non-blocking alert banner upon reaching sentinel thresholds.
   - Circuit breaker on `RESOURCE_EXHAUSTED (code 429)`: pauses downstream swarm launches and alerts the operator instead of spinning in tight retry loops.

4. **Tactile & HUD Telemetry Mesh**:
   - Broadcasts real-time turn deltas and quota statuses to `ws://127.0.0.1:8765/ws` and Cloudflare Workers edge (`aether-pulse-edge.aether-pulse.workers.dev`).
   - Senses underlying desktop windows and browser targets to adapt HUD visualizations.

---

## 2. CLI Tooling Reference

The skill kit bundles standalone executables under `scripts/`:

### A. Telemetry Probe (`aether_agent_probe.py`)
```bash
# FUNCTION: Probe active harness cache hit rates and token volume
# USE_CASE: Turn-by-turn agent diagnostic inspection
python scripts/aether_agent_probe.py status --lens specular
```

Output:
```json
{
  "harness": "Google Antigravity",
  "sessions": 371,
  "total_tokens": "2.18B",
  "cache_hit_pct": 93.82,
  "specular_cost_usd": 244.42,
  "secular_cost_usd": 20.00,
  "spectacular_worth_usd": 6699.00,
  "leverage_index": 26967,
  "status": "NOMINAL"
}
```

### B. Cold Cache Leak Auditor (`aether_agent_probe.py audit`)
```bash
# FUNCTION: Scan transcript logs for cache eviction spikes
# USE_CASE: Detect when uncompacted mega-files force expensive re-writes
python scripts/aether_agent_probe.py audit --threshold 500000
```

### C. System Prompt & Context Optimizer (`cache_optimizer.py`)
```bash
# FUNCTION: Analyze and optimize context ordering for KV-cache reuse
# USE_CASE: Reorder static vs dynamic content to exceed 95% cache hits
python scripts/cache_optimizer.py --target ./prompts/system.md
```

---

## 3. Direct Swarm Directives (`AGENT_INVARIANTS.md`)

When deploying subagents, always inject the companion invariants from:
`templates/AGENT_INVARIANTS.md`

Rules include:
- Zero stock file tampering.
- Cryptographic build parity across workspace, staging, and target deployments.
- Sole author identity attribution to **`Eloquent`** (`@mjeanhudson-dev`).
- Zero local OS username leakage (`Users\<username>` -> `~/` or `%USERPROFILE%`).
