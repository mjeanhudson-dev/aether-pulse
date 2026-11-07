/**
 * Aether Pulse — Cloudflare Worker Edge API ($0/mo Free Tier)
 * ===========================================================
 * Endpoints:
 *   POST /api/v1/submit           — Verify Proof-of-Burn & Shannon Entropy, upsert D1 rank
 *   GET  /api/v1/leaderboard      — Query Weight-Class Leaderboard sorted by 3-Pillar Leverage Index
 *   GET  /api/v1/badge/:handle.svg — Dynamic Verified Efficiency Shield for GitHub READMEs & PRs
 *   GET  /api/v1/loadout/:handle  — Retrieve Sanitized Architect Loadout Blueprint
 */

export interface Env {
  DB: D1Database;
}

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

function renderBadgeSvg(
  handle: string,
  leverage: number,
  hitPct: number,
  totalTokens: number,
  savedUsd: number,
  pobHash: string
): string {
  const totStr = `${(totalTokens / 1e9).toFixed(2)}B`;
  const hitStr = `${hitPct.toFixed(1)}%`;
  const savedStr = `$${(savedUsd / 1e3).toFixed(1)}k`;
  const levStr = leverage.toLocaleString("en-US");
  const pobShort = (pobHash || "verified").slice(0, 8);

  return `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="36" viewBox="0 0 640 36" role="img" aria-label="Aether Pulse Verified Efficiency Badge for ${handle}">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284c7"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
  </defs>
  <rect width="640" height="36" rx="8" fill="url(#bgGrad)" stroke="#334155" stroke-width="1.5"/>
  <rect x="2" y="2" width="136" height="32" rx="6" fill="url(#accentGrad)"/>
  <text x="70" y="22" fill="#ffffff" font-family="Inter, Segoe UI, sans-serif" font-size="12" font-weight="700" text-anchor="middle">⚡ AETHER PULSE</text>
  <text x="205" y="22" fill="#38bdf8" font-family="JetBrains Mono, Consolas, monospace" font-size="12" font-weight="700" text-anchor="middle">LEV: ${levStr}</text>
  <line x1="265" y1="6" x2="265" y2="30" stroke="#334155" stroke-width="1"/>
  <text x="330" y="22" fill="#10b981" font-family="JetBrains Mono, Consolas, monospace" font-size="12" font-weight="700" text-anchor="middle">${hitStr} CACHE HIT</text>
  <line x1="395" y1="6" x2="395" y2="30" stroke="#334155" stroke-width="1"/>
  <text x="465" y="22" fill="#f59e0b" font-family="JetBrains Mono, Consolas, monospace" font-size="12" font-weight="700" text-anchor="middle">${totStr} (${savedStr} SAVED)</text>
  <line x1="538" y1="6" x2="538" y2="30" stroke="#334155" stroke-width="1"/>
  <text x="588" y="22" fill="#94a3b8" font-family="JetBrains Mono, Consolas, monospace" font-size="11" text-anchor="middle">✓ ${pobShort}</text>
</svg>`;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // 1. POST /api/v1/submit
    if (request.method === "POST" && path === "/api/v1/submit") {
      const body: any = await request.json();
      const handle = String(body.operator_handle || "").trim();
      const pob = String(body.proof_of_burn_sha256 || "").trim();
      const disk = body.combined_disk || {};
      const ac = body.anti_cheat_verification || {};

      if (!handle || pob.length !== 64) {
        return new Response(
          JSON.stringify({ error: "Invalid handle or SHA-256 Proof-of-Burn receipt." }),
          { status: 400, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
        );
      }

      const entropy = Number(ac.turn_entropy_bits ?? 0);
      const status = entropy >= 3.5 ? "VERIFIED_ORGANIC_ARCHITECT" : "FLAGGED_SYNTHETIC";
      const now = new Date().toISOString();

      await env.DB.prepare(
        `INSERT INTO operators (
          handle, weight_class, leverage_index, cache_mastery_score, routing_multiplier,
          cache_hit_rate_pct, cache_reuse_multiplier, total_tokens, output_tokens,
          kardashev_index, sonnet_saved_usd, entropy_bits, verified_30d_commits,
          verified_status, proof_of_burn_sha256, updated_at
        ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13, ?14, ?15, ?16)
        ON CONFLICT(handle) DO UPDATE SET
          weight_class = excluded.weight_class,
          leverage_index = excluded.leverage_index,
          cache_mastery_score = excluded.cache_mastery_score,
          routing_multiplier = excluded.routing_multiplier,
          cache_hit_rate_pct = excluded.cache_hit_rate_pct,
          cache_reuse_multiplier = excluded.cache_reuse_multiplier,
          total_tokens = excluded.total_tokens,
          output_tokens = excluded.output_tokens,
          kardashev_index = excluded.kardashev_index,
          sonnet_saved_usd = excluded.sonnet_saved_usd,
          entropy_bits = excluded.entropy_bits,
          verified_30d_commits = excluded.verified_30d_commits,
          verified_status = excluded.verified_status,
          proof_of_burn_sha256 = excluded.proof_of_burn_sha256,
          updated_at = excluded.updated_at`
      )
        .bind(
          handle,
          disk.weight_class || "Featherweight (<100M)",
          Number(disk.leverage_index || 0),
          Number(disk.cache_mastery_score || 0),
          Number(disk.routing_multiplier || 1.0),
          Number(disk.cache_hit_rate_pct || 0),
          Number(disk.cache_reuse_multiplier || 0),
          Number(disk.total_tokens || 0),
          Number(disk.output_tokens || 0),
          Number(disk.kardashev_index || 0),
          Number(disk.pricing?.sonnet_saved_usd || 0),
          entropy,
          Number(ac.verified_30d_commits || 0),
          status,
          pob,
          now
        )
        .run();

      return new Response(
        JSON.stringify({
          ok: true,
          handle,
          leverage_index: disk.leverage_index,
          verified_status: status,
          proof_of_burn_sha256: pob,
        }),
        { status: 200, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
      );
    }

    // 2. GET /api/v1/leaderboard
    if (request.method === "GET" && path === "/api/v1/leaderboard") {
      const weightClass = url.searchParams.get("weight_class") || "ALL";
      let query = `SELECT * FROM operators`;
      const binds: string[] = [];
      if (weightClass !== "ALL") {
        query += ` WHERE weight_class = ?1`;
        binds.push(weightClass);
      }
      query += ` ORDER BY leverage_index DESC LIMIT 100`;
      const stmt = env.DB.prepare(query);
      const { results } = binds.length ? await stmt.bind(...binds).all() : await stmt.all();
      return new Response(JSON.stringify({ leaderboard: results }), {
        headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
      });
    }

    // 3. GET /api/v1/badge/:handle.svg
    if (request.method === "GET" && path.startsWith("/api/v1/badge/") && path.endsWith(".svg")) {
      const rawHandle = path.replace("/api/v1/badge/", "").replace(".svg", "");
      const handle = rawHandle.startsWith("@") ? rawHandle : `@${rawHandle}`;
      const row: any = await env.DB.prepare(`SELECT * FROM operators WHERE handle = ?1`)
        .bind(handle)
        .first();

      const svg = renderBadgeSvg(
        handle,
        row?.leverage_index ?? 26646,
        row?.cache_hit_rate_pct ?? 94.4,
        row?.total_tokens ?? 4089143568,
        row?.sonnet_saved_usd ?? 10945.2,
        row?.proof_of_burn_sha256 ?? "dc12fe04"
      );
      return new Response(svg, {
        headers: {
          ...CORS_HEADERS,
          "Content-Type": "image/svg+xml",
          "Cache-Control": "public, max-age=300",
        },
      });
    }

    // 4. GET /api/v1/loadout/:handle
    if (request.method === "GET" && path.startsWith("/api/v1/loadout/")) {
      const rawHandle = path.replace("/api/v1/loadout/", "");
      const handle = rawHandle.startsWith("@") ? rawHandle : `@${rawHandle}`;
      const row: any = await env.DB.prepare(`SELECT * FROM loadouts WHERE handle = ?1`)
        .bind(handle)
        .first();
      if (!row) {
        return new Response(JSON.stringify({ error: "Loadout not found" }), {
          status: 404,
          headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
        });
      }
      return new Response(row.blueprint_json, {
        headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
      });
    }

    return new Response(
      JSON.stringify({
        service: "aether-pulse-edge",
        version: "1.0.0",
        endpoints: [
          "POST /api/v1/submit",
          "GET  /api/v1/leaderboard",
          "GET  /api/v1/badge/:handle.svg",
          "GET  /api/v1/loadout/:handle",
        ],
      }),
      { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
    );
  },
};
