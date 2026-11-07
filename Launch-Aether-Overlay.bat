@echo off
REM FUNCTION: Launch Aether Pulse Local Desktop Liquid-Physics Overlay & WebSocket Telemetry Server
REM USE_CASE: Run floating topmost HUD over Claude Code, Antigravity, Codex CLI, and T3 Code
title Aether Pulse Liquid HUD Launcher
cd /d "%~dp0"
start "Aether Pulse WebSocket Daemon" /B pythonw aether_pulse_ws.py
start "Aether Pulse Liquid Desktop HUD" /B pythonw aether_liquid_overlay.pyw
if errorlevel 1 (
    python aether_liquid_overlay.py
)
