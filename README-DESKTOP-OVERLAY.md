# Aether Pulse — Local Desktop Liquid-Physics Overlay (`v1.0.0`)

Authored by **Eloquent** (`@mjeanhudson-dev`)

A frameless, topmost Cupertino-styled desktop HUD that floats over any AI terminal, browser, or IDE (`Claude Code`, `Google Antigravity`, `OpenAI Codex CLI`, `T3 Code`, `Windows Terminal`, `VS Code`):

1. **Freefloat Wiggle/Drift + Bounce & Pac-Man Screen Wrap:**
   - Drag and release the liquid-filled vessel to let it drift with real momentum and buoyancy wiggle.
   - Click the bottom-right physics button (`[BNC]` / `[PAC]` / `[PIN]`) to switch between:
     - **`BNC` (Bounce Walls):** Bounces elastically off your monitor edges with a liquid splash.
     - **`PAC` (Pac-Man Wrap):** Flies through bottom-to-top and side-to-side screen edges like Pac-Man.
     - **`PIN` (Pin Anchor):** Settles at the drop coordinate with subtle liquid buoyancy.
2. **Seamless Spatial Harness Detection:**
   - Uses Win32 `WindowFromPoint` + `QueryFullProcessImageNameW` to inspect whichever window is underneath the HUD while dragging or freefloating, morphing displayed `Tokens`, `Cost`, `Cache Hit %`, and `Leverage` automatically.
3. **1-Click Harness Mode Switcher (`[ ≋ AUTO ]`):**
   - Cycles `Auto-Sense Target` -> `All 3 Harnesses Drawer` -> `Claude Code` -> `Antigravity` -> `Codex CLI`.

## Quick Start (Windows / macOS / Linux)

- **1-Click Windows Launch:** Double-click `Launch-Aether-Overlay.bat` or `aether_liquid_overlay.pyw`.
- **CLI Launch:**
  ```powershell
  python aether_pulse_ws.py
  python aether_liquid_overlay.py
  ```
