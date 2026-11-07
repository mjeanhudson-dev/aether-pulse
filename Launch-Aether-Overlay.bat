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
echo     - Header controls: [⚙] Settings modal, [—] Minimize to tray, [✕] Close/dock.
echo     - System Tray: Right-click icon in taskbar for full context menu and restore.
echo     - Side buttons: [MODE] Top 10 cycle, [LGT/DRK] Theme toggle, [BNC] Physics cycle.
echo.
timeout /t 3 >nul
