# Autonomous Agent Swarm Invariants & Cache Mastery Directives

These directives govern all autonomous AI agents, subagent workers, and tool loops operating in the Aether Pulse ecosystem.

---

## 1. Prompt-Cache Prefix Preservation (The Gold Rule)
- **Static Prefix Immutability**:
  Never prepend volatile variables (timestamps, randomized run IDs, temporary paths) to system prompts or root context files.
- **KV-Cache Hit Ceiling**:
  Aim for `>92%` cache hit rates across all turn sequences. Moving static configuration or tool schemas invalidates the entire downstream KV-cache and incurs 10x-20x compute costs.

---

## 2. 3-Lens Accounting Accountability
Every agent session must report token metrics across three explicit lenses:
1. **💎 Specular (API)**: Official Google AI Studio / Anthropic developer pay-as-you-go cost.
2. **👁️ Secular (Flat)**: Worldly out-of-pocket cash paid for monthly subscription seats ($20.00/mo flat).
3. **⚡ Spectacular (Worth)**: Gross market replacement worth delivered across net synthesized code yield and context streams.

---

## 3. Sentinel Quota & 429 Circuit Breakers
- **Daily 10M Token Sentinel**:
  If daily token consumption reaches or exceeds 10,000,000 tokens, emit an immediate alert banner detailing token volume and proceed with high efficiency.
- **HTTP 429 Circuit Breaker**:
  Upon encountering `RESOURCE_EXHAUSTED (code 429)`, DO NOT enter immediate tight retry loops. Pause downstream worker launches, log the offending trajectory, and notify the operator immediately.

---

## 4. Cryptographic Parity & Author Identity
- **Sole Operator & Author Identity**:
  Exclusively attribute code, commits, release tags, and telemetry to **`Eloquent`** (`@mjeanhudson-dev`).
- **Zero OS Username Leakage**:
  Normalize all filesystem paths to `~/` or `%USERPROFILE%`. Never expose local operating system usernames in commits, logs, or published artifacts.
