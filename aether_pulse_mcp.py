#!/usr/bin/env python3
"""
Aether Pulse — Universal MCP Server (aether_pulse_mcp.py)
=========================================================
Zero-dependency Model Context Protocol (MCP) JSON-RPC 2.0 stdio server
for Claude Code, Google Antigravity (Gemini), and OpenAI Codex CLI.

Exposes 4 tools:
  1. get_my_efficiency_rank   — Live 3-Pillar Leverage Index, Weight Class, & Cohort Rank
  2. diagnose_cache_leaks     — Pinpoints sessions with high Cache-Write spikes or low CR/CW
  3. compare_with_cohort      — Benchmarks operator against Featherweight/Cruiserweight/Heavyweight peers
  4. export_loadout_blueprint — Exports secret-scrubbed Architect Spotlight Blueprint (.json + .md)
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import aether_pulse  # noqa: E402


SERVER_INFO = {
    "name": "aether-pulse-mcp",
    "version": "1.0.0",
}

TOOLS_SCHEMA = [
    {
        "name": "get_my_efficiency_rank",
        "description": (
            "Returns the operator's live 3-Pillar Leverage Index, Weight Class "
            "(Featherweight / Cruiserweight / Heavyweight), Cache Mastery score, "
            "Multi-Model Routing multiplier, Shannon Entropy Proof-of-Work status, "
            "and global cohort ranking across Claude Code, Google Antigravity, and OpenAI Codex CLI."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "description": "If true, forces a fresh scan of all local harness JSONL logs before returning.",
                    "default": False,
                }
            },
        },
    },
    {
        "name": "diagnose_cache_leaks",
        "description": (
            "Audits local Claude Code, Google Antigravity, and OpenAI Codex CLI transcripts "
            "for cold-cache write spikes and low cache-reuse sessions, returning actionable "
            "recommendations to raise Cache Hit % and Leverage Index."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of leaky sessions to return (default: 10).",
                    "default": 10,
                }
            },
        },
    },
    {
        "name": "compare_with_cohort",
        "description": (
            "Compares the operator's 3-Pillar Leverage Index, Cache Hit %, and API cost savings "
            "against verified public cohort benchmarks in a specific weight class or across all tiers."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "weight_class": {
                    "type": "string",
                    "description": "Filter cohort by 'Heavyweight', 'Cruiserweight', 'Featherweight', or 'all'.",
                    "default": "all",
                }
            },
        },
    },
    {
        "name": "export_loadout_blueprint",
        "description": (
            "Exports the operator's sanitized Architect Spotlight Loadout Blueprint "
            "(aether_loadout_blueprint.json and AETHER_LOADOUT.md) with automatic secret scrubbing."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def load_or_scan_report(refresh: bool = False) -> Dict[str, Any]:
    report_path = SCRIPT_DIR / "aether_pulse_report.json"
    if not refresh and report_path.exists():
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    report = aether_pulse.scan_local_harnesses()
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def handle_tool_call(name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    args = arguments or {}

    if name == "get_my_efficiency_rank":
        report = load_or_scan_report(refresh=bool(args.get("refresh", False)))
        m = report["combined_disk"]
        ac = report["anti_cheat_verification"]
        board = report.get("leaderboard") or aether_pulse.build_leaderboard_entries(report)
        my_rank = next(
            (r["rank"] for r in board if "3-CLI Trinity" in r.get("handle", "")),
            1,
        )
        payload = {
            "operator_handle": report["operator_handle"],
            "global_cohort_rank": f"#{my_rank} of {len(board)}",
            "weight_class": m["weight_class"],
            "leverage_index": m["leverage_index"],
            "cache_mastery_score": m["cache_mastery_score"],
            "routing_multiplier": f"{m['routing_multiplier']:.2f}x",
            "cache_hit_rate_pct": m["cache_hit_rate_pct"],
            "cache_reuse_multiplier": m["cache_reuse_multiplier"],
            "kardashev_index": m["kardashev_index"],
            "total_tokens": m["total_tokens"],
            "api_value_saved_sonnet_usd": m["pricing"]["sonnet_saved_usd"],
            "anti_cheat_status": ac["status"],
            "entropy_bits": ac["turn_entropy_bits"],
            "verified_git_commits": ac.get("verified_30d_commits", 0),
            "proof_of_burn_sha256": report["proof_of_burn_sha256"],
            "badges": m["badges"],
            "harness_breakdown": {
                "claude_code": report["claude_code"]["total_tokens"],
                "google_antigravity": report["antigravity"]["total_tokens"],
                "openai_codex_cli": report["openai_codex"]["total_tokens"],
            },
        }
        return {
            "content": [{"type": "text", "text": json.dumps(payload, indent=2)}],
            "isError": False,
        }

    elif name == "diagnose_cache_leaks":
        report = load_or_scan_report(refresh=False)
        limit = int(args.get("limit", 10))
        leaks = report.get("cache_doctor_top_leaks", [])[:limit]
        comb = report["combined_disk"]
        recommendations = [
            "Trigger `/compact` before raw uncached input exceeds 150k tokens in long-running sessions.",
            "Avoid pausing >60 minutes mid-session on heavy contexts to prevent 5m/1h prompt-cache TTL eviction spikes.",
            "Delegate broad codebase searches to lightweight subagents (`research` / Flash) so main-thread context stays cached.",
            "Keep static instructions and rules in top-level system files (`CLAUDE.md` / `AGENTS.md`) so the prefix hash remains invariant.",
        ]
        payload = {
            "overall_cache_hit_rate_pct": comb["cache_hit_rate_pct"],
            "overall_cache_reuse_multiplier": comb["cache_reuse_multiplier"],
            "detected_leak_count": len(leaks),
            "leaky_sessions": leaks,
            "optimization_playbook": recommendations,
        }
        return {
            "content": [{"type": "text", "text": json.dumps(payload, indent=2)}],
            "isError": False,
        }

    elif name == "compare_with_cohort":
        report = load_or_scan_report(refresh=False)
        wc_filter = str(args.get("weight_class", "all")).lower()
        board = report.get("leaderboard") or aether_pulse.build_leaderboard_entries(report)
        if wc_filter not in ("all", ""):
            board = [
                r for r in board
                if wc_filter in r["metrics"]["weight_class"].lower() or r.get("highlight")
            ]
        comparison = [
            {
                "rank": r.get("rank", idx + 1),
                "handle": r["handle"],
                "rank_tier": r["rank_tier"],
                "weight_class": r["metrics"]["weight_class"],
                "leverage_index": r["metrics"]["leverage_index"],
                "cache_hit_rate_pct": r["metrics"]["cache_hit_rate_pct"],
                "cache_reuse_multiplier": r["metrics"]["cache_reuse_multiplier"],
                "total_tokens": r["metrics"]["total_tokens"],
                "sonnet_saved_usd": r["metrics"]["pricing"]["sonnet_saved_usd"],
            }
            for idx, r in enumerate(board)
        ]
        return {
            "content": [{"type": "text", "text": json.dumps({"cohort_comparison": comparison}, indent=2)}],
            "isError": False,
        }

    elif name == "export_loadout_blueprint":
        report = load_or_scan_report(refresh=False)
        blueprint = aether_pulse.export_loadout_blueprint(report, SCRIPT_DIR)
        return {
            "content": [{"type": "text", "text": json.dumps(blueprint, indent=2)}],
            "isError": False,
        }

    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "isError": True,
    }


def process_rpc_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params") or {}

    # Notifications (no id) do not receive a response
    if req_id is None:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        }
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS_SCHEMA},
        }
    elif method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments") or {}
        result = handle_tool_call(tool_name, tool_args)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result,
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }


def run_stdio_server() -> None:
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = process_rpc_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


def run_self_test() -> int:
    print("=== Aether Pulse MCP Server Self-Test ===")
    init_resp = process_rpc_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert init_resp and init_resp["result"]["serverInfo"]["name"] == "aether-pulse-mcp"
    tools_resp = process_rpc_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = tools_resp["result"]["tools"]
    assert len(tools) == 4
    print(f"[PASS] Registered {len(tools)} MCP tools: {[t['name'] for t in tools]}")

    for idx, t in enumerate(tools, start=3):
        call_resp = process_rpc_request({
            "jsonrpc": "2.0",
            "id": idx,
            "method": "tools/call",
            "params": {"name": t["name"], "arguments": {}},
        })
        assert call_resp and not call_resp["result"]["isError"]
        print(f"[PASS] tools/call -> {t['name']} succeeded.")
    print("=== ALL MCP SELF-TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(run_self_test())
    run_stdio_server()
