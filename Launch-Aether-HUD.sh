#!/usr/bin/env bash
# FUNCTION: Launch Aether Pulse Universal Liquid HUD on macOS and Linux
# USE_CASE: Starts local WebSocket daemon and opens the hardware-accelerated liquid overlay
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=== Aether Pulse Universal Liquid HUD Launcher ==="
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
else
    echo "Error: Python 3 is required to run Aether Pulse HUD."
    exit 1
fi

"$PY_CMD" launch_hud.py "$@"
