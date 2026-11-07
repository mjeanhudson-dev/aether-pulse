#!/usr/bin/env node
/**
 * Aether Pulse — Universal Cross-Platform Node.js CLI Entrypoint (`npx aether-pulse`)
 * Authored by Eloquent (@mjeanhudson-dev)
 *
 * Delegates CLI commands (`--overlay`, `--ws`, `--mcp`, `--apply-loadout`, or default scan)
 * to the bundled Python multi-harness telemetry engine.
 */

const { spawnSync } = require("child_process");
const path = require("path");

const args = process.argv.slice(2);
const rootDir = path.resolve(__dirname, "..");

let targetScript = "aether_pulse.py";
let forwardArgs = args;

if (args.includes("--ws")) {
  targetScript = "aether_pulse_ws.py";
  forwardArgs = args.filter((a) => a !== "--ws");
} else if (args.includes("--overlay")) {
  targetScript = "aether_liquid_overlay.py";
  forwardArgs = args.filter((a) => a !== "--overlay");
} else if (args.includes("--mcp")) {
  targetScript = "aether_pulse_mcp.py";
  forwardArgs = args.filter((a) => a !== "--mcp");
} else if (args.includes("--install") || args.includes("--apply-loadout") || args.includes("--dry-run")) {
  targetScript = "install_aether_pulse.py";
}

const scriptPath = path.join(rootDir, targetScript);
const pyCmd = process.platform === "win32" ? "python" : "python3";

const res = spawnSync(pyCmd, [scriptPath, ...forwardArgs], {
  stdio: "inherit",
  cwd: rootDir
});

process.exit(res.status !== null ? res.status : 0);
