# CLAUDE.md — Aether Pulse Repository Directives & Design System Rules

- **Public Identity Invariant:** All code, commits, documentation, badges, and leaderboard profiles in this repository are authored by **Eloquent (`@mjeanhudson-dev`)**. Never include local OS usernames or raw personal filesystem paths (`C:\Users\...`) in any tracked file or generated artifact; always normalize paths to `~` or `Path.home()`.
- **Design System Authority:** Read [`DESIGN.md`](./DESIGN.md) and [`PRODUCT.md`](./PRODUCT.md) before modifying any UI surface in `aether_pulse.py` or `aether_pulse_leaderboard.html`.
- **Aesthetic Standard (Cupertino Demure Telemetry):**
  1. Maintain native **Light & Dark Mode** via `<meta name="color-scheme" content="light dark">`, CSS `light-dark()`, and the tri-state segmented controller (`System` / `Light` / `Dark`).
  2. **Zero Color-to-Color Transitions:** Never introduce linear gradients on text or badges, neon accent colors, thick colored side-borders, or emoji icons. Use tonal surface elevation, `1px` hairline dividers, and `1.5px`-stroke inline SVGs.
  3. **High-Resolution Optical Legibility:** Keep body text at `16px` (`1rem`), table cells at `15px` (`0.9375rem`) with `tabular-nums`, and ledger figures at `38px` (`2.375rem`) with `-0.03em` tracking.
- **Verification Gate:** Run `python -m unittest discover -s tests -v` and `python aether_pulse_mcp.py --self-test` before every commit.
