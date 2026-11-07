#!/usr/bin/env python3
"""
Aether Pulse Universal Desktop Liquid HUD Launcher
===================================================
Author: Eloquent (@mjeanhudson-dev)

Cross-platform desktop runner for Windows, macOS, and Linux:
1. Native Frameless Transparent Webview (via pywebview + Edge WebView2 / WebKit / WebKit2GTK).
2. Standalone Zero-Chrome App Window fallback (via Chrome / Edge / Chromium / Brave --app).
Backbacked by local asynchronous WebSocket telemetry server on `127.0.0.1:8765`.
"""

import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request

HUD_URL = "http://127.0.0.1:8765/hud"
WS_SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aether_pulse_ws.py")


def is_server_alive(timeout: float = 0.5) -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8765/api/telemetry", timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def ensure_ws_server_running() -> None:
    if is_server_alive():
        return
    print("[Aether HUD] Starting local WebSocket & Telemetry daemon...")
    if sys.platform == "win32":
        subprocess.Popen(
            [sys.executable, WS_SERVER_SCRIPT],
            creationflags=getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
            close_fds=True,
        )
    else:
        subprocess.Popen(
            [sys.executable, WS_SERVER_SCRIPT],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    for _ in range(30):
        time.sleep(0.15)
        if is_server_alive():
            print("[Aether HUD] WebSocket & Telemetry daemon active on ws://127.0.0.1:8765/ws")
            return


class HudJsApi:
    """Exposes native OS window actions to hud.html JavaScript."""

    def __init__(self, window=None) -> None:
        self.window = window

    def set_window(self, window) -> None:
        self.window = window

    def close(self) -> None:
        if self.window:
            self.window.destroy()

    def minimize(self) -> None:
        if self.window:
            self.window.minimize()

    def set_on_top(self, on_top: bool) -> None:
        if self.window:
            self.window.on_top = bool(on_top)


def launch_via_pywebview(force_browser: bool = False) -> bool:
    if force_browser:
        return False
    try:
        import webview

        api = HudJsApi()
        window = webview.create_window(
            title="Aether Pulse — Liquid Telemetry HUD",
            url=HUD_URL,
            js_api=api,
            width=424,
            height=216,
            frameless=True,
            easy_drag=True,
            on_top=True,
            transparent=True,
            background_color="#00000000",
            draggable=True,
            text_select=False,
            zoomable=False,
            vibrancy=True,
        )
        api.set_window(window)
        print("[Aether HUD] Launching GPU-composited hardware-antialiased HUD via pywebview...")
        webview.start(private_mode=False)
        return True
    except Exception as exc:
        print(f"[Aether HUD] pywebview startup skipped ({exc}); engaging standalone app runner...")
        return False


def find_browser_app_executable() -> str:
    system = platform.system()
    candidates = []

    if system == "Windows":
        local_app = os.environ.get("LOCALAPPDATA", "")
        prog_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        prog = os.environ.get("ProgramFiles", "C:\\Program Files")
        candidates = [
            os.path.join(prog_x86, "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(prog, "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(prog, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(prog_x86, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(local_app, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(prog, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            shutil.which("msedge.exe") or "",
            shutil.which("chrome.exe") or "",
        ]
    elif system == "Darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            shutil.which("google-chrome") or "",
            shutil.which("chromium") or "",
        ]
    else:  # Linux / Unix
        candidates = [
            shutil.which("google-chrome") or "",
            shutil.which("google-chrome-stable") or "",
            shutil.which("chromium") or "",
            shutil.which("chromium-browser") or "",
            shutil.which("brave-browser") or "",
            shutil.which("microsoft-edge") or "",
        ]

    for p in candidates:
        if p and os.path.isfile(p):
            return p
    return ""


def launch_via_browser_app() -> None:
    exe = find_browser_app_executable()
    if not exe:
        print(f"[Aether HUD] Opening default browser to {HUD_URL}...")
        import webbrowser
        webbrowser.open(HUD_URL)
        return

    cmd = [
        exe,
        f"--app={HUD_URL}",
        "--window-size=424,216",
        "--class=AetherPulseHUD",
        "--disable-features=Translate",
    ]
    print(f"[Aether HUD] Launching standalone app container: {exe}")
    subprocess.Popen(cmd)


def main() -> None:
    ensure_ws_server_running()
    force_browser = "--browser" in sys.argv
    if not launch_via_pywebview(force_browser):
        launch_via_browser_app()


if __name__ == "__main__":
    main()
