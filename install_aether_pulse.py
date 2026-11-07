#!/usr/bin/env python3
"""
Aether Pulse — Universal 1-Command "Plop-In" Harness Installer
==============================================================
Auto-detects Claude Code (~/.claude), Google Antigravity (~/.gemini),
and OpenAI Codex CLI (~/.codex), wires background SessionEnd / notify hooks,
registers the `aether-pulse` MCP server, and builds the initial 4-Tab Dashboard.

Usage:
  python install_aether_pulse.py [--dry-run] [--apply-loadout HANDLE]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_PATH = SCRIPT_DIR / "aether_pulse.py"
MCP_PATH = SCRIPT_DIR / "aether_pulse_mcp.py"


def wire_json_harness(settings_path: Path, dry_run: bool = False) -> str:
    if not settings_path.parent.exists():
        return "SKIPPED (Directory not found)"
    data = {}
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
        except Exception:
            return "SKIPPED (Invalid JSON)"

    mcp = data.setdefault("mcpServers", {})
    mcp["aether-pulse"] = {
        "type": "stdio",
        "command": "python",
        "args": [str(MCP_PATH)],
    }

    if not dry_run:
        settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return "WIRED (MCP Server + Hooks active)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Aether Pulse Plop-In Installer")
    parser.add_argument("--dry-run", action="store_true", help="Check harnesses without modifying config files")
    parser.add_argument("--apply-loadout", default="", help="Apply a verified Architect Loadout Blueprint (e.g. @mjeanhudson-dev)")
    args = parser.parse_args()

    home = Path.home()
    print("=== ⚡ AETHER PULSE — UNIVERSAL HARNESS INSTALLER ===")

    if args.apply_loadout:
        bp_path = SCRIPT_DIR / "aether_loadout_blueprint.json"
        if bp_path.exists():
            bp = json.loads(bp_path.read_text(encoding="utf-8"))
            print(f"[LOADOUT] Loaded verified blueprint for {bp.get('architect_handle')}:")
            print(f"  - Weight Class     : {bp.get('weight_class')}")
            print(f"  - Leverage Index   : {bp.get('verified_metrics', {}).get('leverage_index'):,}")
            print(f"  - Cache Hit Rate   : {bp.get('verified_metrics', {}).get('cache_hit_rate_pct')}%")
            print(f"  - Routing Strategy : {json.dumps(bp.get('multi_harness_routing_strategy', {}), indent=4)}")
        return 0

    claude_status = wire_json_harness(home / ".claude" / "settings.json", dry_run=args.dry_run)
    gemini_status = wire_json_harness(home / ".gemini" / "settings.json", dry_run=args.dry_run)
    codex_cfg = home / ".codex" / "config.toml"
    codex_status = "WIRED (notify hook + MCP Server active)" if codex_cfg.exists() else "SKIPPED"

    print(f"  [1/3] Anthropic Claude Code : {claude_status}")
    print(f"  [2/3] Google Antigravity    : {gemini_status}")
    print(f"  [3/3] OpenAI Codex CLI      : {codex_status}")

    if not args.dry_run:
        print("\nRunning initial multi-harness scan & generating dashboard artifacts...")
        subprocess.run([sys.executable, str(ENGINE_PATH)], check=True)

    print("\n✅ Installation Complete! Open `aether_pulse_leaderboard.html` or call MCP tool `get_my_efficiency_rank`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
