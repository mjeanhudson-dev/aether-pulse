#!/usr/bin/env python3
"""
Automated Unit & Integration Test Suite for Aether Pulse v1.0
=============================================================
Tests:
  1. Weight Class assignment (Featherweight, Cruiserweight, Heavyweight)
  2. 3-Pillar Leverage Index rewards high Cache Hit % & Routing over raw uncached burn
  3. Shannon Entropy Anti-Cheat catches synthetic `while true` loops (< 3.5 bits)
  4. Secret Scrubbing in `export_loadout_blueprint` strips API keys/tokens
  5. SVG Shield generation produces valid SVG with Proof-of-Burn hash
  6. MCP Server JSON-RPC 2.0 protocol (`initialize`, `tools/list`, and all 4 `tools/call`)
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import aether_pulse  # noqa: E402
import aether_pulse_mcp  # noqa: E402


class TestAetherPulseEngine(unittest.TestCase):
    def test_weight_class_tiers(self):
        self.assertEqual(aether_pulse.determine_weight_class(45_000_000), "Featherweight (<100M)")
        self.assertEqual(aether_pulse.determine_weight_class(420_000_000), "Cruiserweight (100M-1B)")
        self.assertEqual(aether_pulse.determine_weight_class(4_089_000_000), "Heavyweight (1B+)")

    def test_leverage_index_rewards_efficiency_over_uncached_burn(self):
        # Efficient architect: 94.5% cache hit, 1.24x multi-harness routing, organic entropy
        efficient = aether_pulse.compute_metrics(
            inp=120_000_000,
            cr=3_800_000_000,
            cw=100_000_000,
            out=28_000_000,
            routing_multiplier=1.24,
            entropy_bits=4.2,
        )
        # Wasteful uncached burner: 55% cache hit, single-model 1.0x routing, synthetic loop entropy
        wasteful = aether_pulse.compute_metrics(
            inp=2_500_000_000,
            cr=3_500_000_000,
            cw=500_000_000,
            out=10_000_000,
            routing_multiplier=1.00,
            entropy_bits=2.1,
        )
        self.assertGreater(
            efficient["leverage_index"],
            wasteful["leverage_index"],
            "Efficient 94.5% cache architect must outrank wasteful uncached loop burner on Leverage Index!",
        )

    def test_shannon_entropy_anti_cheat(self):
        # Synthetic `while true` loop with identical 4096-token turns
        synthetic_deltas = [4096] * 200
        syn_entropy = aether_pulse.compute_shannon_entropy(synthetic_deltas)
        self.assertLess(syn_entropy, 1.0)

        # Organic multi-turn engineering session with diverse token deltas
        organic_deltas = [
            150, 420, 1200, 3400, 8900, 15400, 28000, 45000,
            62000, 95000, 130000, 185000, 240000, 310000, 520, 1800,
        ] * 5
        org_entropy = aether_pulse.compute_shannon_entropy(organic_deltas)
        self.assertGreaterEqual(org_entropy, 3.5)

    def test_svg_badge_and_loadout_secret_scrubbing(self):
        report = aether_pulse.scan_local_harnesses()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            svg_path = tmp_dir / "badge.svg"
            aether_pulse.generate_svg_badge(report, svg_path)
            svg_text = svg_path.read_text(encoding="utf-8")
            self.assertIn("<svg", svg_text)
            self.assertIn("Aether Pulse", svg_text)
            self.assertIn(report["proof_of_burn_sha256"][:8], svg_text)

            blueprint = aether_pulse.export_loadout_blueprint(report, tmp_dir)
            bp_str = json.dumps(blueprint)
            # Ensure no sensitive API_KEY or SECRET leaked into the exported blueprint
            self.assertNotIn("GEMINI_API_KEY", bp_str)
            self.assertIn("multi_harness_routing_strategy", blueprint)

    def test_public_identity_scrub_and_apple_theme_compliance(self):
        report = aether_pulse.scan_local_harnesses()
        os_user = Path.home().name.lower()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            svg_path = tmp_dir / "badge.svg"
            html_path = tmp_dir / "leaderboard.html"
            aether_pulse.generate_svg_badge(report, svg_path)
            blueprint = aether_pulse.export_loadout_blueprint(report, tmp_dir)
            aether_pulse.generate_html_dashboard(report, blueprint, html_path)

            report_str = json.dumps(report)
            bp_str = json.dumps(blueprint)
            md_str = (tmp_dir / "AETHER_LOADOUT.md").read_text(encoding="utf-8")
            html_str = html_path.read_text(encoding="utf-8")
            svg_str = svg_path.read_text(encoding="utf-8")

            for artifact_name, content in [
                ("report.json", report_str),
                ("blueprint.json", bp_str),
                ("AETHER_LOADOUT.md", md_str),
                ("leaderboard.html", html_str),
                ("badge.svg", svg_str),
            ]:
                self.assertNotIn(
                    os_user,
                    content.lower(),
                    f"Personal OS username leaked into public artifact {artifact_name}!",
                )

            self.assertEqual(report.get("operator_name"), "Eloquent")
            self.assertIn("Eloquent", html_str)
            self.assertIn('<meta name="color-scheme" content="light dark">', html_str)
            self.assertIn("light-dark(", html_str)
            self.assertIn('role="region"', html_str)

    def test_mcp_json_rpc_tools(self):
        init_res = aether_pulse_mcp.process_rpc_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
        })
        self.assertEqual(init_res["result"]["serverInfo"]["name"], "aether-pulse-mcp")

        list_res = aether_pulse_mcp.process_rpc_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
        })
        tool_names = [t["name"] for t in list_res["result"]["tools"]]
        self.assertEqual(
            tool_names,
            [
                "get_my_efficiency_rank",
                "diagnose_cache_leaks",
                "compare_with_cohort",
                "export_loadout_blueprint",
            ],
        )

        for idx, tname in enumerate(tool_names, start=10):
            call_res = aether_pulse_mcp.process_rpc_request({
                "jsonrpc": "2.0",
                "id": idx,
                "method": "tools/call",
                "params": {"name": tname, "arguments": {}},
            })
            self.assertFalse(call_res["result"]["isError"], f"MCP tool {tname} returned error")
            parsed = json.loads(call_res["result"]["content"][0]["text"])
            self.assertIsInstance(parsed, dict)

    def test_t3_usage_analytics_and_svg_charts(self):
        report = aether_pulse.scan_local_harnesses()
        t3 = aether_pulse.build_t3_usage_analytics(report)
        self.assertIn("tier_mix", t3)
        self.assertIn("token_composition", t3)
        self.assertIn("trajectory", t3)
        self.assertGreaterEqual(len(t3["trajectory"]), 12)
        self.assertGreater(t3["cost_arbitrage"]["compression_pct"], 90.0)
        self.assertIn("CREATE PROPERTY GRAPH", t3["bigquery_property_graph_ddl"])

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            html_path = tmp_dir / "leaderboard.html"
            blueprint = aether_pulse.export_loadout_blueprint(report, tmp_dir)
            aether_pulse.generate_html_dashboard(report, blueprint, html_path)
            html_str = html_path.read_text(encoding="utf-8")
            self.assertIn('id="t3-usage-board"', html_str)
            self.assertIn('id="trajectory-svg-chart"', html_str)
            self.assertIn('id="aether-liquid-hud"', html_str)
            self.assertIn('id="hud-side-CycleBtn"', html_str)

    def test_websocket_telemetry_and_harness_target_detection(self):
        import aether_pulse_ws

        self.assertEqual(
            aether_pulse_ws.detect_harness_from_context("Claude Code - bash", "WindowsTerminal.exe", ""),
            "claude_code",
        )
        self.assertEqual(
            aether_pulse_ws.detect_harness_from_context("Antigravity - aether-pulse", "Antigravity.exe", ""),
            "antigravity",
        )
        self.assertEqual(
            aether_pulse_ws.detect_harness_from_context("OpenAI Codex CLI Sandbox", "codex.exe", "https://chatgpt.com/codex"),
            "openai_codex",
        )

        # RFC 6455 frame round-trip
        payload = json.dumps({"event": "harness_switch", "harness": "antigravity"}).encode("utf-8")
        frame = aether_pulse_ws.encode_ws_frame(payload)
        opcode, decoded = aether_pulse_ws.decode_ws_frame(frame)
        self.assertEqual(opcode, 1)
        self.assertEqual(decoded, payload)

        # 1-button side mode cycling
        self.assertEqual(aether_pulse_ws.next_overlay_mode("auto"), "all")
        self.assertEqual(aether_pulse_ws.next_overlay_mode("all"), "claude_code")
        self.assertEqual(aether_pulse_ws.next_overlay_mode("claude_code"), "antigravity")
        self.assertEqual(aether_pulse_ws.next_overlay_mode("antigravity"), "openai_codex")
        self.assertEqual(aether_pulse_ws.next_overlay_mode("openai_codex"), "auto")

    def test_liquid_physics_solver_and_chrome_extension_manifest_v3(self):
        import aether_pulse_ws

        state = aether_pulse_ws.create_liquid_physics_state(x=100.0, y=100.0, num_nodes=9)
        state = aether_pulse_ws.step_liquid_physics(state, target_x=320.0, target_y=180.0, dt=0.016)
        # Spring-mass inertia: position moves smoothly toward target without teleporting
        self.assertGreater(state["x"], 100.0)
        self.assertLess(state["x"], 320.0)
        self.assertNotEqual(state["tilt_deg"], 0.0)
        self.assertGreater(max(abs(w) for w in state["wave_heights"]), 0.0)

        ext_dir = PROJECT_DIR / "chrome-extension"
        manifest_path = ext_dir / "manifest.json"
        self.assertTrue(manifest_path.exists(), "chrome-extension/manifest.json must exist")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_version"], 3)
        self.assertIn("action", manifest)
        self.assertIn("storage", manifest["permissions"])
        self.assertIn("tabs", manifest["permissions"])

        # Verify real PNG dimensions for 16, 48, 128 icons
        for size in (16, 48, 128):
            icon_rel = manifest["icons"][str(size)]
            icon_file = ext_dir / icon_rel
            self.assertTrue(icon_file.exists(), f"Missing extension icon {icon_rel}")
            raw = icon_file.read_bytes()
            self.assertEqual(raw[:8], b"\x89PNG\r\n\x1a\n")
            w = int.from_bytes(raw[16:20], "big")
            h = int.from_bytes(raw[20:24], "big")
            self.assertEqual((w, h), (size, size))

        self.assertTrue((PROJECT_DIR / "CHROMEWEBSTORE.md").exists())


if __name__ == "__main__":
    unittest.main()
