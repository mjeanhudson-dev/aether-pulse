# Aether Pulse — Design System Rules & Figma MCP Specification
**Author:** Eloquent (`@mjeanhudson-dev`)  
**Architecture:** Apple Cupertino Demure / Obsidian Dark Glass  
**Target Environments:** Web Dashboard (HTML5/CSS3), Native Desktop Liquid Overlay (Python/Tkinter/Win32), and Edge API (Cloudflare Workers D1)

---

## 1. Token Definitions

### Location of Design Tokens
- **Web Platform:** Defined as native CSS Custom Properties on `:root` inside [`aether_pulse.py`](./aether_pulse.py) (compiled into [`index.html`](./index.html) and [`aether_pulse_leaderboard.html`](./aether_pulse_leaderboard.html)).
- **Desktop Runtime:** Structured dictionary constants inside [`aether_liquid_overlay.py`](./aether_liquid_overlay.py) (`THEME_PALETTES['dark']` and `THEME_PALETTES['light']`).

### Token Structure & Naming Conventions
Tokens follow semantic functional roles rather than raw color names:

```css
:root {
  color-scheme: light dark;

  /* Surfaces & Canvas */
  --bg-canvas-light: #F5F5F7;
  --bg-canvas-dark: #000000;
  --bg-surface-light: #FFFFFF;
  --bg-surface-dark: #121214;
  --bg-elevated-light: #F0F0F3;
  --bg-elevated-dark: #1C1C1E;

  /* Typography Colors */
  --text-primary-light: #1D1D1F;
  --text-primary-dark: #FFFFFF;
  --text-secondary-light: #5A5A60;
  --text-secondary-dark: #A1A1A6;
  --text-muted-light: #8E8E93;
  --text-muted-dark: #75757C;

  /* Borders & Dividers */
  --border-hairline-light: rgba(0, 0, 0, 0.08);
  --border-hairline-dark: #2C2C2E;
  --border-divider-glow: #1A365D;

  /* Restrained Accents */
  --accent-light: #0066CC;
  --accent-dark: #2997FF;
  --crest-glow-dark: #388BFF;
  --status-pinned: #30D158;
  --status-drifting: #FF9F0A;
  --status-wrapping: #0A84FF;

  /* Liquid Horizon Dynamics */
  --fluid-back-dark: #0D1826;
  --fluid-front-dark: #13273D;
  --fluid-back-light: #DCEAF7;
  --fluid-front-light: #C8E1FA;
}
```

### Token Transformation System
- **CSS `light-dark()` Function:** Uses native modern CSS `light-dark(var(--light), var(--dark))` for dynamic zero-runtime switching.
- **Python Bridge:** `THEME_PALETTES[self.theme]` dynamically binds colors to Tkinter canvas polygons and Win32 hardware clipped regions.

---

## 2. Component Library

### Core UI Components
1. **Floating Liquid Telemetry Capsule (`AetherLiquidDesktopOverlay`):**
   - Width: `464px`
   - Height: `114px` (Compact) / `184px` (Expanded Drawer)
   - Corner Fillet: `24px` true Win32 hardware clipping (`CreateRoundRectRgn`)
   - 2-Button Right Rail: Mode switcher (`≋ ALL 3`) and Physics anchor (`PIN` / `BNC` / `PAC`)
2. **Hero Telemetry Ledger Strip:**
   - Unified 4-column card row (Leverage Index, 3-Harness Volume, Cache Hit %, Retail Compute Saved).
3. **Interactive Spline Charts (`#trajectory-svg-chart`):**
   - Monotone cubic splines (Fritsch-Carlson algorithm) with interactive mouse scrobbler. Zero circle dots.
4. **Segmented Controller Tab Bar:**
   - Tabs: Leaderboard, T3 Usage Graphs, Bounty Board, Sub Tiers (Unoemono -> Quap), Platform Comparison, Cache Doctor.

---

## 3. Frameworks & Libraries
- **Web UI:** Vanilla HTML5, modern CSS3 (Custom Properties, Grid, Flexbox, backdrop-filter), ES2024 (native WebSockets, zero React/Vue overhead).
- **Desktop HUD:** Pure Python 3.10+ standard library (`tkinter`, `ctypes`, `json`, `webbrowser`, `math`). Zero heavy GUI dependencies.
- **Serverless Edge:** Cloudflare Workers, D1 SQL database, Wrangler.
- **Local WebSocket Telemetry:** `aether_pulse_ws.py` (pure standard library HTTP & RFC 6455 WebSocket server).

---

## 4. Asset Management
- **Vector Assets:** All icons, badges, and charts are generated as mathematically pure inline SVGs or rendered dynamically via canvas lines.
- **Static Shields:** [`aether_pulse_badge.svg`](./aether_pulse_badge.svg) (Proof-of-Burn cryptographic efficiency shield).
- **Desktop Bundles:** [`AetherPulse-Desktop-Overlay.zip`](./AetherPulse-Desktop-Overlay.zip) packaged autonomously for offline distribution.

---

## 5. Icon System
- **Minimalist Glyphs:** Unicode typography-first iconography to guarantee zero asset loading latency:
  - `≋` (Liquid Wave / Multi-Harness Mode)
  - `●` (Status Indicator Dot)
  - `✓` (Verified Organic Architect Checkmark)
  - `💎` (Specular API Accounting Lens)
  - `👁️` (Secular Flat Cash Accounting Lens)
  - `⚡` (Spectacular Frontier Value Accounting Lens)
  - `📌` (Always on Top / Pinned Anchor)
  - `🖥️` (4K Desktop Studio Dashboard)

---

## 6. Styling Approach
- **Cupertino Restraint:** Strictly no rainbow gradients, no cartoonish drop shadows, and no visual clutter.
- **Optical Typography:** `SF Pro Display` / `Segoe UI Variable Display` for headers; `SF Mono` / `Cascadia Code` for tabular figures.
- **Volumetric Liquid:** 2-layer parallax undercurrent with a smooth Catmull-Rom specular meniscus crest.

---

## 7. Project Structure
```text
aether-pulse/
├── aether_pulse.py                 # Core telemetry engine & HTML generator
├── aether_pulse_ws.py              # WebSocket & HTTP telemetry server
├── aether_liquid_overlay.py        # Native Desktop Floating Liquid HUD
├── aether_liquid_overlay.pyw       # Windowless desktop HUD entrypoint
├── Launch-Aether-Overlay.bat       # 1-click desktop overlay launcher
├── Launch-Aether-Studio.bat        # 1-click native Edge app studio launcher
├── index.html                      # Standalone 4K analytical web dashboard
├── aether_pulse_leaderboard.html   # Compiled leaderboard artifact
├── AetherPulse-Desktop-Overlay.zip # Distributable standalone desktop bundle
├── DESIGN_SYSTEM_RULES.md          # Figma MCP Design System Rules
├── DESIGN.md                       # Design tokens & architectural principles
├── CLAUDE.md                       # Repo directives & author identity
├── package.json                    # npm package configuration (v1.1.2)
└── tests/
    └── test_aether_pulse.py        # Automated test suite (100% pass)
```
