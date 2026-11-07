#!/usr/bin/env python3
"""
Aether Pulse — Native Desktop & Terminal Floating Liquid-Physics Overlay (`aether_liquid_overlay.py`)
======================================================================================================
Authored by Eloquent (@mjeanhudson-dev)

A frameless, topmost Cupertino-styled desktop HUD that floats over any AI terminal or IDE
(Claude Code, Google Antigravity, OpenAI Codex CLI, Cursor, Aider, Windsurf, Continue.dev,
GitHub Copilot, OpenHands, T3 Code, Windows Terminal, Chrome):
  1. Weighty Liquid-Filled Drag + Freefloat Drift/Wiggle Physics:
     Uses `aether_pulse_ws.step_liquid_physics` with 48 spring nodes, 2nd-order spring-mass-damper,
     and unnatural viscous eddy braking when flung at high speeds.
  2. Fluid Wall Splashes & Waves:
     Wall collisions excite violent directional surges along the impact flank, spraying dynamic
     droplet particles that fall under simulated gravity.
  3. Native Win32 Rounded Window Frame:
     Clips the frameless window with `CreateRoundRectRgn` / `SetWindowRgn` for native rounded corners.
  4. Light / Dark Mode Toggle (`☀️ LGT` / `🌙 DRK`):
     Dedicated tactile button on the right control column, switching complete color palettes
     and translucent liquid horizons.
  5. Top 10 Ecosystem Harnesses Support:
     Continuously probes the foreground/underlying window to detect all 10 major agent harnesses
     from Google search & GitHub.
  6. Elevated Typography:
     Uses `Segoe UI Variable Display` micro-caps, `Cascadia Code` / `Consolas` tabular figures,
     and crisp secondary hierarchies.
"""

from __future__ import annotations

import ctypes
import math
import random
import sys
import time
import tkinter as tk
import tkinter.font as tkfont
from typing import Any, Dict, List, Optional, Tuple

import aether_pulse
import aether_pulse_ws

BOUNDARY_SHORT = {
    "bounce": "BNC",
    "pacman": "PAC",
    "pin": "PIN",
}

THEME_PALETTES = {
    "dark": {
        "bg": "#121214",
        "surface": "#1A1A1E",
        "border": "#2C2C2E",
        "header": "#F5F5F7",
        "primary_text": "#FFFFFF",
        "secondary_text": "#A1A1A6",
        "subtle_text": "#75757C",
        "button_bg": "#1C1C1E",
        "button_border": "#3A3A3C",
        "divider": "#2C2C2E",
        "fluid_back": "#0D1826",
        "fluid_front": "#13273D",
        "crest_glow": "#388BFF",
        "particle_color": "#E5E5EA",
    },
    "light": {
        "bg": "#F8F8FA",
        "surface": "#FFFFFF",
        "border": "#E5E5EA",
        "header": "#1D1D1F",
        "primary_text": "#000000",
        "secondary_text": "#5A5A60",
        "subtle_text": "#8E8E93",
        "button_bg": "#FFFFFF",
        "button_border": "#D1D1D6",
        "divider": "#E5E5EA",
        "fluid_back": "#DCEAF7",
        "fluid_front": "#C8E1FA",
        "crest_glow": "#0066CC",
        "particle_color": "#0066CC",
    },
}


class SplashParticle:
    def __init__(self, x: float, y: float, vx: float, vy: float, size: float, color: str) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.life = 1.0  # Fades from 1.0 to 0.0

    def step(self, dt: float, gravity: float = 520.0) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += gravity * dt
        self.life -= dt * 2.2
        return self.life > 0.0


class AetherLiquidDesktopOverlay:
    def __init__(self) -> None:
        self.report = aether_pulse.scan_local_harnesses()
        self.mode = "auto"
        self.boundary_mode = "bounce"
        self.theme = "dark"
        self.detected_harness = "all"
        self.target_label = "Desktop Workspace"
        self.particles: List[SplashParticle] = []

        self.root = tk.Tk()
        self.root.title("Aether Pulse Liquid HUD")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.96)

        palette = THEME_PALETTES[self.theme]
        self.root.configure(bg=palette["bg"])

        self.screen_w = float(max(800, self.root.winfo_screenwidth()))
        self.screen_h = float(max(600, self.root.winfo_screenheight()))

        self.width = 418
        self.height = 114
        self.target_x = 140.0
        self.target_y = 140.0
        self.corner_radius = 24

        self.phys = aether_pulse_ws.create_liquid_physics_state(
            x=self.target_x,
            y=self.target_y,
            num_nodes=48,
            boundary_mode=self.boundary_mode,
            width=float(self.width),
            height=float(self.height),
        )
        # Seed gentle initial freefloat drift so the vessel feels alive immediately
        self.phys["vx"] = 54.0
        self.phys["vy"] = 32.0
        self.root.geometry(f"{self.width}x{self.height}+{int(self.target_x)}+{int(self.target_y)}")

        self._init_fonts()

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=palette["bg"],
            highlightthickness=1,
            highlightbackground=palette["border"],
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._drag_offset_x = 0
        self._drag_offset_y = 0
        self._is_dragging = False
        self._last_t = time.perf_counter()
        self._last_probe_t = 0.0
        self._last_ptr_x = 0.0
        self._last_ptr_y = 0.0
        self._last_ptr_t = time.perf_counter()
        self._throw_vx = 0.0
        self._throw_vy = 0.0

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Apply native Windows 11 rounded window region
        self.root.update_idletasks()
        self._apply_rounded_window_region()

        self._tick()

    def _init_fonts(self) -> None:
        try:
            families = set(tkfont.families(self.root))
        except Exception:
            families = set()

        self.font_display = "Segoe UI Variable Display" if "Segoe UI Variable Display" in families else "Segoe UI"
        self.font_text = "Segoe UI Variable Text" if "Segoe UI Variable Text" in families else "Segoe UI"
        self.font_mono = "Cascadia Code" if "Cascadia Code" in families else ("Consolas" if "Consolas" in families else "Courier")

    def _apply_rounded_window_region(self) -> None:
        if sys.platform != "win32":
            return
        try:
            hwnd = self.root.winfo_id()
            rgn = ctypes.windll.gdi32.CreateRoundRectRgn(
                0, 0, self.width + 1, self.height + 1, self.corner_radius, self.corner_radius
            )
            ctypes.windll.user32.SetWindowRgn(hwnd, rgn, True)
        except Exception:
            pass

    def _toggle_theme(self) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"
        palette = THEME_PALETTES[self.theme]
        self.root.configure(bg=palette["bg"])
        self.canvas.configure(bg=palette["bg"], highlightbackground=palette["border"])

    def _on_press(self, event: tk.Event) -> None:
        col_w = 56
        btn_x_start = self.width - col_w

        # Check if click landed on the right-side control column
        if event.x >= btn_x_start:
            section_h = self.height / 3.0
            if event.y < section_h:
                # Top Button: Cycle Mode (Auto -> All -> Top 10 Harnesses)
                self.mode = aether_pulse_ws.next_overlay_mode(self.mode)
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] += 48.0
                self._update_height_for_mode()
            elif event.y < section_h * 2.0:
                # Middle Button: Toggle Light / Dark Theme
                self._toggle_theme()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] -= 32.0
            else:
                # Bottom Button: Cycle Boundary Mode (BNC -> PAC -> PIN)
                self.boundary_mode = aether_pulse_ws.next_boundary_mode(self.boundary_mode)
                self.phys["boundary_mode"] = self.boundary_mode
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] += 36.0
                if self.boundary_mode in ("bounce", "pacman") and math.hypot(self.phys["vx"], self.phys["vy"]) < 30.0:
                    self.phys["vx"] = 68.0
                    self.phys["vy"] = -42.0
            return

        self._is_dragging = True
        self._drag_offset_x = event.x
        self._drag_offset_y = event.y
        self._last_ptr_x = float(self.root.winfo_pointerx())
        self._last_ptr_y = float(self.root.winfo_pointery())
        self._last_ptr_t = time.perf_counter()
        self._throw_vx = 0.0
        self._throw_vy = 0.0

    def _on_drag(self, _event: tk.Event) -> None:
        if not self._is_dragging:
            return
        now = time.perf_counter()
        px = float(self.root.winfo_pointerx())
        py = float(self.root.winfo_pointery())
        dt_ptr = max(0.004, now - self._last_ptr_t)
        inst_vx = (px - self._last_ptr_x) / dt_ptr
        inst_vy = (py - self._last_ptr_y) / dt_ptr
        self._throw_vx = 0.65 * self._throw_vx + 0.35 * inst_vx
        self._throw_vy = 0.65 * self._throw_vy + 0.35 * inst_vy
        self._last_ptr_x = px
        self._last_ptr_y = py
        self._last_ptr_t = now

        self.target_x = px - self._drag_offset_x
        self.target_y = py - self._drag_offset_y
        self._probe_underneath(now, force=True)

    def _on_release(self, _event: tk.Event) -> None:
        if not self._is_dragging:
            return
        self._is_dragging = False
        # Preserve throw momentum on release so it drifts/wiggles and bounces or Pac-Man wraps
        # Notice: When thrown at high speed (>180 px/s), step_liquid_physics applies unnatural viscous eddy braking!
        throw_spd = math.hypot(self._throw_vx, self._throw_vy)
        scale = 0.62 if throw_spd < 350.0 else 0.48
        self.phys["vx"] = max(-920.0, min(920.0, self._throw_vx * scale + (52.0 if abs(self._throw_vx) < 20.0 else 0.0)))
        self.phys["vy"] = max(-920.0, min(920.0, self._throw_vy * scale + (-36.0 if abs(self._throw_vy) < 20.0 else 0.0)))
        self.target_x = float(self.phys["x"])
        self.target_y = float(self.phys["y"])

    def _probe_underneath(self, now: float, force: bool = False) -> None:
        if not force and (now - self._last_probe_t) < 0.14:
            return
        self._last_probe_t = now
        probe_x = int(self.phys["x"] + self.width // 2)
        probe_y = int(self.phys["y"] + self.height + 12)
        probed = aether_pulse_ws.probe_window_at_point(probe_x, probe_y, ignore_hwnd=self.root.winfo_id())
        self.detected_harness = probed["detected_harness"]
        if probed["window_title"]:
            self.target_label = probed["window_title"][:34]
        elif probed.get("process_name"):
            self.target_label = probed["process_name"][:34]

    def _update_height_for_mode(self) -> None:
        self.height = 240 if self.mode == "all" else 114
        self.phys["height"] = float(self.height)
        self.canvas.config(height=self.height)
        self.root.update_idletasks()
        self._apply_rounded_window_region()

    def _spawn_splash_particles(self, side: str, impulse: float, accent_hex: str) -> None:
        count = min(22, max(8, int(impulse * 0.16)))
        body_w = self.width - 56
        palette = THEME_PALETTES[self.theme]

        for _ in range(count):
            if side == "left":
                px = random.uniform(2.0, 18.0)
                py = random.uniform(self.height * 0.35, self.height * 0.85)
                vx = random.uniform(30.0, 160.0)
                vy = random.uniform(-240.0, -60.0)
            elif side == "right":
                px = random.uniform(body_w - 18.0, body_w - 2.0)
                py = random.uniform(self.height * 0.35, self.height * 0.85)
                vx = random.uniform(-160.0, -30.0)
                vy = random.uniform(-240.0, -60.0)
            else:
                px = random.uniform(10.0, body_w - 10.0)
                py = random.uniform(self.height * 0.6, self.height - 6.0)
                vx = random.uniform(-80.0, 80.0)
                vy = random.uniform(-190.0, -40.0)

            size = random.uniform(1.8, 3.6)
            color = accent_hex if random.random() > 0.4 else palette["particle_color"]
            self.particles.append(SplashParticle(px, py, vx, vy, size, color))

    def _tick(self) -> None:
        now = time.perf_counter()
        dt = now - self._last_t
        self._last_t = now

        aether_pulse_ws.step_liquid_physics(
            self.phys,
            self.target_x,
            self.target_y,
            dt=dt,
            is_dragging=self._is_dragging,
            bounds_w=self.screen_w,
            bounds_h=self.screen_h,
        )

        # Trigger splash particle emission if a wall collision occurred
        splash_event = self.phys.get("splash_event")
        if splash_event:
            side = splash_event.get("side", "left")
            impulse = float(splash_event.get("impulse", 50.0))
            frame_preview = aether_pulse_ws.build_ws_telemetry_frame(
                self.report, self.mode, self.detected_harness, self.target_label, self.boundary_mode
            )
            accent = frame_preview["active"]["accent_hex"]
            self._spawn_splash_particles(side, impulse, accent)

        # Step dynamic splash particles
        alive_particles: List[SplashParticle] = []
        for p in self.particles:
            if p.step(dt):
                alive_particles.append(p)
        self.particles = alive_particles

        if not self._is_dragging:
            self.target_x = float(self.phys["x"])
            self.target_y = float(self.phys["y"])
            self._probe_underneath(now, force=False)

        cx = int(round(self.phys["x"]))
        cy = int(round(self.phys["y"]))
        self.root.geometry(f"{self.width}x{self.height}+{cx}+{cy}")

        self._render()
        self.root.after(16, self._tick)

    def _render(self) -> None:
        frame = aether_pulse_ws.build_ws_telemetry_frame(
            self.report,
            self.mode,
            self.detected_harness,
            self.target_label,
            self.boundary_mode,
        )
        active = frame["active"]
        fill_ratio = float(active["liquid_fill_ratio"])
        palette = THEME_PALETTES[self.theme]

        self.canvas.delete("all")

        body_w = self.width - 56
        base_y = self.height - (self.height * 0.44 * fill_ratio)
        waves = self.phys["wave_heights"]
        n = len(waves)
        tilt = float(self.phys["tilt_deg"])

        # 1. Back wave layer (translucent parallax depth)
        back_pts = [0, self.height]
        for i, h in enumerate(waves):
            px = (i / max(1, n - 1)) * body_w
            # Slight phase & amplitude difference for parallax wave feel
            back_h = h * 0.7 + math.sin(float(self.phys["phase"]) * 2.8 + i * 0.28) * 2.2
            py = max(8.0, min(self.height - 2.0, base_y - 4.0 + back_h + (tilt * ((i - n / 2) * 0.38))))
            back_pts.extend([px, py])
        back_pts.extend([body_w, self.height])
        self.canvas.create_polygon(back_pts, fill=palette["fluid_back"], outline="", smooth=True)

        # 2. Front wave layer (primary fluid mass)
        front_pts = [0, self.height]
        for i, h in enumerate(waves):
            px = (i / max(1, n - 1)) * body_w
            py = max(10.0, min(self.height - 2.0, base_y + h + (tilt * ((i - n / 2) * 0.45))))
            front_pts.extend([px, py])
        front_pts.extend([body_w, self.height])
        self.canvas.create_polygon(front_pts, fill=palette["fluid_front"], outline="", smooth=True)

        # 3. Specular liquid meniscus crest line (high-fidelity smoothed wave crest)
        line_pts = front_pts[2:-2]
        if len(line_pts) >= 4:
            self.canvas.create_line(line_pts, fill=active["accent_hex"], width=2.4, smooth=True)

        # 4. Dynamic splash droplet particles
        for p in self.particles:
            r = max(1.0, p.size * p.life)
            self.canvas.create_oval(
                p.x - r,
                p.y - r,
                p.x + r,
                p.y + r,
                fill=p.color,
                outline="",
            )

        # 5. Header: Micro-caps uppercase category & harness name
        self.canvas.create_oval(14, 15, 23, 24, fill=active["accent_hex"], outline="")
        badge_text = f"{active['name'].upper()}  ·  {active.get('model_badge', 'AI Coding Engine')}"
        self.canvas.create_text(
            30,
            19,
            anchor="w",
            text=badge_text[:46],
            fill=palette["header"],
            font=(self.font_display, 8, "bold"),
        )

        # 6. Primary Metric: Tabular Figures
        metric_str = f"{active['tokens_formatted']} TOK    ${active['cost_usd']:,.2f}    {active['cache_hit_pct']}% HIT"
        self.canvas.create_text(
            14,
            49,
            anchor="w",
            text=metric_str,
            fill=palette["primary_text"],
            font=(self.font_mono, 11, "bold"),
        )

        # 7. Subtitle / Spatial Context Line
        sub_str = f"OVER: {frame['target_label'][:24]}   {frame['boundary_mode_label'].upper()}   SAVED ${active['saved_usd']:,}"
        self.canvas.create_text(
            14,
            79,
            anchor="w",
            text=sub_str,
            fill=palette["secondary_text"],
            font=(self.font_text, 8),
        )

        # 8. If "All 10 Harnesses" drawer is open, render 2-column comparative grid
        if frame["show_all_drawer"]:
            self.canvas.create_line(14, 98, body_w - 14, 98, fill=palette["divider"], width=1)
            y_base = 114
            top_harness_keys = [
                "claude_code",
                "antigravity",
                "openai_codex",
                "cursor",
                "aider",
                "windsurf",
                "continue_dev",
                "github_copilot",
                "openhands",
                "t3_code",
            ]
            # 2 columns of 5 rows
            col1 = top_harness_keys[:5]
            col2 = top_harness_keys[5:]

            for row_i, (k1, k2) in enumerate(zip(col1, col2)):
                cur_y = y_base + (row_i * 24)

                # Col 1
                h1 = frame["harnesses"].get(k1, active)
                self.canvas.create_oval(14, cur_y - 4, 20, cur_y + 2, fill=h1["accent_hex"], outline="")
                txt1 = f"{h1['short_name'][:10]:<10} {h1['tokens_formatted']:>6} · {h1['cache_hit_pct']}%"
                self.canvas.create_text(
                    24, cur_y, anchor="w", text=txt1, fill=palette["primary_text"], font=(self.font_mono, 8)
                )

                # Col 2
                h2 = frame["harnesses"].get(k2, active)
                col2_x = 196
                self.canvas.create_oval(col2_x, cur_y - 4, col2_x + 6, cur_y + 2, fill=h2["accent_hex"], outline="")
                txt2 = f"{h2['short_name'][:10]:<10} {h2['tokens_formatted']:>6} · {h2['cache_hit_pct']}%"
                self.canvas.create_text(
                    col2_x + 10, cur_y, anchor="w", text=txt2, fill=palette["primary_text"], font=(self.font_mono, 8)
                )

        # 9. Right-Edge 3-Button Control Column
        self.canvas.create_line(body_w, 0, body_w, self.height, fill=palette["divider"], width=1)
        btn_x = body_w + 6
        btn_w = self.width - 6
        h3 = self.height / 3.0

        # Button 1 (Top): Harness Mode Switcher
        self.canvas.create_rectangle(btn_x, 6, btn_w, int(h3 - 2), fill=palette["button_bg"], outline=palette["button_border"])
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 0.35),
            text="≋",
            fill=palette["header"],
            font=(self.font_display, 10, "bold"),
        )
        mode_abbr = self.mode[:4].upper()
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 0.72),
            text=mode_abbr,
            fill=palette["secondary_text"],
            font=(self.font_mono, 7, "bold"),
        )

        # Button 2 (Middle): Light / Dark Theme Switcher
        self.canvas.create_rectangle(btn_x, int(h3 + 2), btn_w, int(h3 * 2.0 - 2), fill=palette["button_bg"], outline=palette["button_border"])
        theme_icon = "☀️" if self.theme == "light" else "🌙"
        theme_label = "LGT" if self.theme == "light" else "DRK"
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 1.35),
            text=theme_icon,
            fill=palette["header"],
            font=(self.font_display, 9),
        )
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 1.72),
            text=theme_label,
            fill="#FF9F0A" if self.theme == "light" else "#5E5CE6",
            font=(self.font_mono, 7, "bold"),
        )

        # Button 3 (Bottom): Boundary Physics Mode (BNC / PAC / PIN)
        self.canvas.create_rectangle(btn_x, int(h3 * 2.0 + 2), btn_w, self.height - 6, fill=palette["button_bg"], outline=palette["button_border"])
        b_tag = BOUNDARY_SHORT.get(self.boundary_mode, "BNC")
        b_color = "#30D158" if self.boundary_mode == "bounce" else ("#FF9F0A" if self.boundary_mode == "pacman" else palette["subtle_text"])
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 2.5),
            text=b_tag,
            fill=b_color,
            font=(self.font_mono, 8, "bold"),
        )

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        phys = aether_pulse_ws.create_liquid_physics_state(100, 100, num_nodes=48, boundary_mode="bounce")
        phys["vx"] = 520.0
        phys["vy"] = -310.0
        for _ in range(40):
            aether_pulse_ws.step_liquid_physics(phys, 240, 160, 0.016, is_dragging=False, bounds_w=500.0, bounds_h=300.0)
        print(
            "Desktop Liquid Overlay physics smoke test OK:",
            f"x={phys['x']}",
            f"y={phys['y']}",
            f"tilt={phys['tilt_deg']}",
            f"nodes={len(phys['wave_heights'])}",
            f"bounces={phys['wall_bounces']}",
            f"splash={phys.get('splash_event')}",
        )
    else:
        AetherLiquidDesktopOverlay().run()
