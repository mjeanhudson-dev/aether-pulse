-- Aether Pulse — $0/mo Cloudflare D1 (SQLite Edge) Schema
-- Supports Weight-Class Leaderboards, Anti-Cheat Proof-of-Burn Receipts,
-- Sanitized Loadout Blueprints, and Weekly/Monthly Architect Spotlights.

CREATE TABLE IF NOT EXISTS operators (
    handle TEXT PRIMARY KEY,
    github_id TEXT,
    weight_class TEXT NOT NULL,
    leverage_index INTEGER NOT NULL DEFAULT 0,
    cache_mastery_score REAL NOT NULL DEFAULT 0.0,
    routing_multiplier REAL NOT NULL DEFAULT 1.0,
    cache_hit_rate_pct REAL NOT NULL DEFAULT 0.0,
    cache_reuse_multiplier REAL NOT NULL DEFAULT 0.0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    kardashev_index REAL NOT NULL DEFAULT 0.0,
    sonnet_saved_usd REAL NOT NULL DEFAULT 0.0,
    entropy_bits REAL NOT NULL DEFAULT 0.0,
    verified_30d_commits INTEGER NOT NULL DEFAULT 0,
    verified_status TEXT NOT NULL DEFAULT 'VERIFIED_ORGANIC_ARCHITECT',
    proof_of_burn_sha256 TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_operators_leverage
    ON operators (leverage_index DESC);

CREATE INDEX IF NOT EXISTS idx_operators_weight_leverage
    ON operators (weight_class, leverage_index DESC);

CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    handle TEXT NOT NULL,
    proof_of_burn_sha256 TEXT NOT NULL UNIQUE,
    leverage_index INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    entropy_bits REAL NOT NULL,
    payload_json TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    FOREIGN KEY (handle) REFERENCES operators(handle)
);

CREATE TABLE IF NOT EXISTS loadouts (
    handle TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL DEFAULT '1.0.0',
    blueprint_json TEXT NOT NULL,
    clones_count INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (handle) REFERENCES operators(handle)
);

CREATE TABLE IF NOT EXISTS spotlights (
    period_key TEXT PRIMARY KEY, -- e.g. '2026-W45' or '2026-11'
    handle TEXT NOT NULL,
    title TEXT NOT NULL,
    video_walkthrough_url TEXT,
    summary_markdown TEXT NOT NULL,
    featured_at TEXT NOT NULL,
    FOREIGN KEY (handle) REFERENCES operators(handle)
);
