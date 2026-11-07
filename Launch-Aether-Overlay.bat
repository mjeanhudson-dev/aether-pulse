@echo off
REM FUNCTION: Launch Aether Pulse Local Desktop Liquid-Physics Overlay & WebSocket Telemetry Server
REM USE_CASE: Run floating topmost HUD over Claude Code, Antigravity, Codex CLI, and T3 Code
title Aether Pulse Liquid HUD Launcher
cd /d "%~dp0"

echo ==============================================================
echo    ⚡ AETHER PULSE — LIQUID PHYSICS TOPMOST DESKTOP HUD
echo ==============================================================
echo [1/2] Starting WebSocket Telemetry Daemon on 127.0.0.1:8765...
start "Aether Pulse WS Daemon" /B pythonw aether_pulse_ws.py

echo [2/2] Launching Liquid Overlay Window...
start "Aether Pulse Liquid Desktop HUD" pythonw aether_liquid_overlay.pyw
if errorlevel 1 (
    echo [!] pythonw encountered an issue; falling back to python...
    start "Aether Pulse Liquid Desktop HUD" python aether_liquid_overlay.py
)

echo.
echo [✓] Aether Pulse Liquid HUD is now floating on your screen!
echo     - Drag the capsule over any terminal/IDE to auto-sense top 10 harnesses.
echo     - Click [MODE] (Top) to cycle: Claude, Antigravity, Codex, Cursor, Aider, Windsurf, Continue, Copilot, OpenHands, T3, All 10.
echo     - Click [LGT/DRK] (Middle) to toggle Light and Dark visual themes.
echo     - Click [BNC] (Bottom) to cycle physics: Wall Bounce (BNC) / Pac-Man Wrap (PAC) / Pinned Anchor (PIN).
echo.
timeout /t 3 >nul
