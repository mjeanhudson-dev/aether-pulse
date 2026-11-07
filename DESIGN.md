# DESIGN.md & CLAUDE.md — Aether Pulse Cupertino Demure Design System Rules

This document defines the canonical design system rules, token architecture, and Figma MCP integration standards for **Aether Pulse**, authored by **Eloquent (`@mjeanhudson-dev`)**.

---

## 1. Token Definitions

### Where Design Tokens Are Defined
All design tokens are defined as native CSS Custom Properties on `:root` inside [`aether_pulse.py`](./aether_pulse.py) (which compiles into [`aether_pulse_leaderboard.html`](./aether_pulse_leaderboard.html) and [`index.html`](./index.html)).

### Token Format & Light/Dark Transformation System
Tokens use the Baseline CSS `light-dark()` function paired with `<meta name="color-scheme" content="light dark">` and `:root:has(> head > meta[name="color-scheme"][content="dark"])` overrides, plus `@media (prefers-color-scheme: dark)` fallbacks:

```css
:root {
  color-scheme: light dark;

  /* Raw Tonal Palette (Cupertino Daylight vs. Pro Display XDR Midnight) */
  --bg-canvas-light: #F5F5F7;
  --bg-canvas-dark: #000000;
  --bg-surface-light: #FFFFFF;
  --bg-surface-dark: #141416;
  --bg-elevated-light: #F0F0F3;
  --bg-elevated-dark: #1C1C1E;

  --text-primary-light: #1D1D1F;
  --text-primary-dark: #F5F5F7;
  --text-secondary-light: #515154;
  --text-secondary-dark: #A1A1A6;
  --text-muted-light: #6E6E73;
  --text-muted-dark: #86868B;

  --border-hairline-light: rgba(0, 0, 0, 0.08);
  --border-hairline-dark: rgba(255, 255, 255, 0.10);

  /* Single Restrained System Accent (10% Rule — Zero Rainbow Transitions) */
  --accent-light: #0066CC;
  --accent-dark: #2997FF;
  --verified-light: #1D7A3E;
  --verified-dark: #30D158;

  /* Resolved Semantic Tokens via light-dark() */
  --bg-canvas: light-dark(var(--bg-canvas-light), var(--bg-canvas-dark));
  --bg-surface: light-dark(var(--bg-surface-light), var(--bg-surface-dark));
  --bg-elevated: light-dark(var(--bg-elevated-light), var(--bg-elevated-dark));
  --text-primary: light-dark(var(--text-primary-light), var(--text-primary-dark));
  --text-secondary: light-dark(var(--text-secondary-light), var(--text-secondary-dark));
  --text-muted: light-dark(var(--text-muted-light), var(--text-muted-dark));
  --border-hairline: light-dark(var(--border-hairline-light), var(--border-hairline-dark));
  --accent: light-dark(var(--accent-light), var(--accent-dark));
  --verified: light-dark(var(--verified-light), var(--verified-dark));
}
```

### Typography & Optical Resolution Scale
- **Primary Sans (`--font-sans`):** `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", system-ui, sans-serif`
- **Technical Mono (`--font-mono`):** `"SF Mono", "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`
- **Role Scale (Fluid against `--p-scale: 1`):**
  - Display Ledger Value: `2.375rem` (`38px`), weight `600`, tracking `-0.03em`, `font-variant-numeric: tabular-nums`
  - Page Title (`h1`): `1.75rem` (`28px`), weight `600`, tracking `-0.025em`, `text-wrap: balance`
  - Section Heading (`h2`/`h3`): `1.25rem` (`20px`), weight `600`, tracking `-0.015em`
  - Body & Prose: `1rem` (`16px`), line-height `1.6`, measure `60ch–70ch`, `text-wrap: pretty`
  - Data Table Cells: `0.9375rem` (`15px`), line-height `1.45`, `font-variant-numeric: tabular-nums`
  - Metadata & Column Headers: `0.8125rem` (`13px`), weight `500`, tracking `0.01em`

---

## 2. Component Library

Components are authored as semantic, zero-dependency HTML5 + CSS structures inside [`aether_pulse.py`](./aether_pulse.py):
1. **Frosted Glass Top Navigation Bar (`.nav-shell`):** Translucent header (`backdrop-filter: saturate(180%) blur(20px)`) housing the brand mark, verification status, and the **Tri-State Theme Segmented Control (`System` / `Light` / `Dark`)**.
2. **Unified Telemetry Ledger Strip (`.ledger-strip`):** A single elevated surface divided by `1px` hairline vertical rules (`border-inline-end: 1px solid var(--border-hairline)`) displaying the 4 primary metrics without loud multi-colored cards.
3. **Segmented View Switcher & Pill Filters (`.segmented-tabs`, `.filter-pills`):** Tactile Apple-style segmented controls with active pill elevation (`0 1px 3px rgba(0,0,0,0.08)`).
4. **Accessible Responsive Data Table (`.table-region`):** Uses `tabindex="0" role="region" aria-labelledby="..."`, sticky `<thead>` and row `<th>` elements, and `@container (width < 760px)` card-stack transformation.

---

## 3. Frameworks & Libraries
- **Runtime:** Zero external JS/CSS framework dependencies. Pure Baseline HTML5, modern CSS (`light-dark()`, `@container`, `:has()`), and vanilla ES2024 JavaScript.
- **Backend / Edge:** Python 3.12+ stdlib (`aether_pulse.py`, `aether_pulse_mcp.py`) and Cloudflare Workers TypeScript (`cloud/worker.ts` + D1 SQLite `cloud/schema.sql`).

---

## 4. Asset Management
- **Dynamic Vector Shield ([`aether_pulse_badge.svg`](./aether_pulse_badge.svg)):** Self-contained SVG rendered with matching graphite/alabaster aesthetics and zero external font requests.
- **Zero-FOUC Theme Script:** Synchronous `<script>` immediately following `<meta name="color-scheme" content="light dark">` in `<head>`.

---

## 5. Icon System
- **Strict No-Emoji Policy:** Per `impeccable/craft-floor.md`, Unicode emoji are never used as UI icons.
- **Inline Monoline SVG Icons:** All icons use inline `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">` so they inherit `currentColor` seamlessly across Light and Dark modes.

---

## 6. Styling Approach
- **Restraint Over Color Arbitrage:** Hierarchy is achieved through scale, font weight (`400` / `500` / `600`), tabular alignment, and tonal surface contrast—never color-to-color gradients or saturated neon text.
- **Browser Surface Harmonization:** Customizes `::selection`, `scrollbar-color`, `scrollbar-width: thin`, and `:focus-visible` rings from the semantic palette.

---

## 7. Project Structure
- `aether_pulse.py` — Core telemetry scanner, 3-Pillar Leverage Index calculator, sanitizer, SVG generator, and HTML compiler.
- `aether_pulse_mcp.py` — Universal JSON-RPC 2.0 stdio MCP server.
- `install_aether_pulse.py` — 1-command multi-harness installer.
- `cloud/worker.ts` & `cloud/schema.sql` — `$0/mo` Cloudflare Worker + D1 edge leaderboard backend.
- `tests/test_aether_pulse.py` — Automated unit, anti-cheat, identity-scrub, and theme compliance test suite.
