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

import hashlib
import hmac
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

HOME = Path.home()
_SERVER_FILE_PATH = Path(__file__).resolve()
BOOT_CODE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
DEFAULT_CLOUD_MCP_URL = "https://alpha-mcp-mxnmqsr7gq-ue.a.run.app/mcp"

SCRIPT_DIR = _SERVER_FILE_PATH.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import aether_pulse  # noqa: E402

SUPPORTED_PROTOCOL_VERSIONS = [
    "2026-07-28",
    "2025-11-25",
    "2025-06-18",
    "2025-03-26",
    "2024-11-05",
]

SERVER_INFO = {
    "name": "aether-pulse-mcp",
    "version": "1.0.1",
}


def _public_path(raw: str) -> str:
    home_str = str(HOME)
    text = str(raw or "")
    if text.lower().startswith(home_str.lower()):
        return ("~" + text[len(home_str):]).replace("\\", "/")
    return text.replace("\\", "/")


def _env_bi(primary: str, secondary: str, default: str = "") -> str:
    for key in (primary, secondary):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return default


def is_flash_shunt_engaged() -> bool:
    return _env_bi("AETHER_FLASH_SHUNT", "NEXUS_FLASH_SHUNT", "1").lower() not in ("0", "false", "no", "off")


def get_min_model() -> str:
    return _env_bi("AETHER_MIN_MODEL", "NEXUS_MIN_MODEL", "gemini-4-hydrogen-xhigh")


def get_reasoning_effort() -> str:
    return _env_bi("AETHER_REASONING_EFFORT", "NEXUS_REASONING_EFFORT", "high")


def get_vertex_model() -> str:
    return _env_bi("AETHER_VERTEX_MODEL", "NEXUS_VERTEX_MODEL", "gemini-4-carbon")


def get_stage0_vault_db() -> str:
    return _env_bi("AETHER_STAGE0_VAULT_DB", "ALPHA_MCP_VAULT_DB", "")


def get_cloud_mcp_url() -> str:
    return _env_bi("AETHER_CLOUD_MCP_URL", "ALPHA_MCP_CLOUD_URL", DEFAULT_CLOUD_MCP_URL)


def get_platform_env_summary() -> Dict[str, Any]:
    vault_raw = get_stage0_vault_db()
    vault_disp = _public_path(str(Path(vault_raw).expanduser())) if vault_raw else "~/alpha-mcp/mcp_alpha_vault.sqlite3"
    return {
        "flash_shunt": "1" if is_flash_shunt_engaged() else "0",
        "flash_shunt_engaged": is_flash_shunt_engaged(),
        "min_model": get_min_model(),
        "reasoning_effort": get_reasoning_effort(),
        "vertex_model": get_vertex_model(),
        "stage0_vault_db": vault_disp,
        "cloud_mcp_url": get_cloud_mcp_url(),
    }


def get_runtime_parity_attestation() -> Dict[str, Any]:
    try:
        disk_sha = hashlib.sha256(_SERVER_FILE_PATH.read_bytes()).hexdigest()
    except OSError:
        disk_sha = ""
    return {
        "boot_code_sha256": BOOT_CODE_SHA256,
        "disk_code_sha256": disk_sha,
        "runtime_parity_ok": bool(disk_sha) and hmac.compare_digest(BOOT_CODE_SHA256, disk_sha),
    }

def _ann(title: str, read_only: bool = True) -> Dict[str, Any]:
    return {
        "title": title,
        "readOnlyHint": read_only,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }

TOOLS_SCHEMA = [
    {
        "name": "get_my_efficiency_rank",
        "annotations": _ann("Get My Efficiency Rank", read_only=True),
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
        "annotations": _ann("Diagnose Cache Leaks", read_only=True),
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
        "annotations": _ann("Compare With Cohort", read_only=True),
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
        "annotations": _ann("Export Loadout Blueprint", read_only=False),
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

PROMPTS_SCHEMA = [
    {
        "name": "pulse_audit",
        "description": (
            "Run a 3-Pillar Aether Pulse token-efficiency, cache-leak, and cohort-rank audit "
            "across Claude Code, Google Antigravity, and OpenAI Codex CLI."
        ),
        "arguments": [
            {
                "name": "weight_class",
                "description": "Optional cohort filter ('Heavyweight', 'Cruiserweight', 'Featherweight', or 'all').",
                "required": False,
            },
            {
                "name": "limit",
                "description": "Optional maximum number of cache-leak sessions to inspect (default: 10).",
                "required": False,
            },
        ],
    }
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
            **get_runtime_parity_attestation(),
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
            "platform_env": get_platform_env_summary(),
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
            "Offload broad codebase scans to Stage 0 deterministic local scripts (`mcp_carbon_ingest.py` / `stage0_ast_slice_and_parity`) or `inherit`-tier research subagents (Flash shunted) so main-thread context stays cached.",
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
    raw_params = req.get("params")
    params = raw_params if isinstance(raw_params, dict) else {}

    # Notifications (no id) do not receive a response
    if req_id is None:
        return None

    if method == "initialize":
        req_ver = str(params.get("protocolVersion") or "").strip()
        neg_ver = req_ver if req_ver in SUPPORTED_PROTOCOL_VERSIONS else "2024-11-05"
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": neg_ver,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "prompts": {"listChanged": False},
                },
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
        raw_args = params.get("arguments")
        tool_args = raw_args if isinstance(raw_args, dict) else {}
        result = handle_tool_call(tool_name, tool_args)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result,
        }
    elif method == "prompts/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"prompts": PROMPTS_SCHEMA},
        }
    elif method == "prompts/get":
        pname = str(params.get("name") or "").strip()
        raw_pargs = params.get("arguments")
        p_args = raw_pargs if isinstance(raw_pargs, dict) else {}
        if pname in ("pulse_audit", "pulse-audit"):
            wc = str(p_args.get("weight_class") or "").strip() or "all"
            lim = str(p_args.get("limit") or "").strip() or "10"
            prompt_text = (
                f"Run an Aether Pulse 3-Pillar telemetry & cache-hygiene audit (cohort='{wc}', leak_limit={lim}):\n"
                "1. Call `get_my_efficiency_rank` to verify `runtime_parity_ok=true`, 3-Pillar Leverage Index, Cache Mastery, and Proof-of-Burn SHA-256.\n"
                f"2. Call `diagnose_cache_leaks` (`limit={lim}`) to pinpoint cold-cache write spikes and low CR/CW sessions.\n"
                f"3. Call `compare_with_cohort` (`weight_class='{wc}'`) while keeping Flash tiers shunted (`flash_shunt={'1' if is_flash_shunt_engaged() else '0'}`, floor `{get_min_model()}`, effort `{get_reasoning_effort()}`)."
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "description": PROMPTS_SCHEMA[0]["description"],
                    "messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}],
                },
            }
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32602, "message": f"Unknown prompt: {pname}"},
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
    global SCRIPT_DIR
    print("=== Aether Pulse MCP Server Self-Test ===")
    for pver in SUPPORTED_PROTOCOL_VERSIONS:
        init_resp = process_rpc_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": pver},
        })
        assert init_resp and init_resp["result"]["serverInfo"]["name"] == "aether-pulse-mcp"
        assert init_resp["result"]["protocolVersion"] == pver
        assert "prompts" in init_resp["result"]["capabilities"]
    tools_resp = process_rpc_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = tools_resp["result"]["tools"]
    assert len(tools) == 4
    assert all(isinstance(t.get("annotations", {}).get("readOnlyHint"), bool) for t in tools)
    print(f"[PASS] Registered {len(tools)} MCP tools: {[t['name'] for t in tools]}")

    prompts_resp = process_rpc_request({"jsonrpc": "2.0", "id": 2, "method": "prompts/list"})
    assert prompts_resp and [p["name"] for p in prompts_resp["result"]["prompts"]] == ["pulse_audit"]
    for pparams in ({"name": "pulse_audit"}, {"name": "pulse_audit", "arguments": None}, {"name": "pulse_audit", "arguments": {}}):
        pg = process_rpc_request({"jsonrpc": "2.0", "id": 2, "method": "prompts/get", "params": pparams})
        assert pg and "result" in pg and pg["result"]["messages"][0]["content"]["text"]
    print("[PASS] Verified nil-arg-safe prompts/list and prompts/get (pulse_audit).")

    saved_env = {k: os.environ.get(k) for k in ("AETHER_MIN_MODEL", "NEXUS_MIN_MODEL", "AETHER_VERTEX_MODEL", "NEXUS_VERTEX_MODEL", "AETHER_CLOUD_MCP_URL", "ALPHA_MCP_CLOUD_URL")}
    try:
        for k in saved_env:
            os.environ.pop(k, None)
        os.environ["NEXUS_MIN_MODEL"] = "gemini-4-neon-high"
        os.environ["NEXUS_VERTEX_MODEL"] = "gemini-4-neon"
        os.environ["ALPHA_MCP_CLOUD_URL"] = "https://example.run.app/mcp"
        assert get_min_model() == "gemini-4-neon-high"
        assert get_vertex_model() == "gemini-4-neon"
        assert get_cloud_mcp_url() == "https://example.run.app/mcp"
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    orig_script_dir = SCRIPT_DIR
    with tempfile.TemporaryDirectory(prefix="aether_pulse_selftest_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        cached_report = orig_script_dir / "aether_pulse_report.json"
        if cached_report.is_file():
            shutil.copy2(cached_report, tmp_path / "aether_pulse_report.json")
        SCRIPT_DIR = tmp_path
        try:
            for idx, t in enumerate(tools, start=3):
                call_resp = process_rpc_request({
                    "jsonrpc": "2.0",
                    "id": idx,
                    "method": "tools/call",
                    "params": {"name": t["name"], "arguments": {}},
                })
                assert call_resp and not call_resp["result"]["isError"]
                if t["name"] == "get_my_efficiency_rank":
                    rank_obj = json.loads(call_resp["result"]["content"][0]["text"])
                    assert rank_obj["boot_code_sha256"] == BOOT_CODE_SHA256
                    assert rank_obj["disk_code_sha256"] == BOOT_CODE_SHA256
                    assert rank_obj["runtime_parity_ok"] is True
                print(f"[PASS] tools/call -> {t['name']} succeeded.")
        finally:
            SCRIPT_DIR = orig_script_dir
    print("=== ALL MCP SELF-TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--selftest" in sys.argv:
        sys.exit(run_self_test())
    run_stdio_server()
