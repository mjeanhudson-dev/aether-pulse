@echo off
title Aether Pulse Studio Launcher
cd /d "%~dp0"
echo [Aether Pulse] Starting local telemetry WebSocket service...
start "" pythonw.exe aether_pulse_ws.py
timeout /t 1 /nobreak >nul
echo [Aether Pulse] Launching Standalone Desktop Studio Window...
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="http://127.0.0.1:8765/" --window-size=1440,900 --window-position=120,60
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --app="http://127.0.0.1:8765/" --window-size=1440,900 --window-position=120,60
) else (
    start "" http://127.0.0.1:8765/
)
